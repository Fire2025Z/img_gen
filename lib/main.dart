import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Image Generator',
      theme: ThemeData(
        primaryColor: Color(0xFFcf8bfc),
        scaffoldBackgroundColor: Colors.black,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.black,
          elevation: 0,
          centerTitle: true,
          iconTheme: IconThemeData(color: Color(0xFFcf8bfc)),
        ),
        textTheme: TextTheme(
          displayLarge: TextStyle(
            color: Color(0xFFcf8bfc),
            fontSize: 28,
            fontWeight: FontWeight.w700,
          ),
          bodyLarge: TextStyle(
            color: Colors.white,
            fontSize: 16,
          ),
          bodyMedium: TextStyle(
            color: Colors.white70,
            fontSize: 14,
          ),
          labelLarge: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Color(0xFF1a1a1a),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: Color(0xFFcf8bfc).withOpacity(0.3)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: BorderSide(color: Color(0xFFcf8bfc)),
          ),
          hintStyle: TextStyle(color: Colors.white54),
          labelStyle: TextStyle(color: Color(0xFFcf8bfc)),
          contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Color(0xFFcf8bfc),
            foregroundColor: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            padding: EdgeInsets.symmetric(vertical: 18),
            textStyle: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.5,
            ),
          ),
        ),
        cardTheme: CardThemeData(
          color: Color(0xFF1a1a1a),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        dividerTheme: DividerThemeData(
          color: Color(0xFFcf8bfc).withOpacity(0.2),
          thickness: 1,
          space: 20,
        ),
      ),
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _controller = TextEditingController();
  bool _loading = false;
  Uint8List? _image;

  Future<void> _generate() async {
    if (_controller.text.isEmpty) return;
    
    setState(() {
      _loading = true;
      _image = null;
    });

    try {
      // Try different URLs based on where you're running
      final urls = [
        'http://10.0.2.2:8000/generate',  // Android emulator
        'http://localhost:8000/generate', // iOS simulator
      ];
      
      http.Response? response;
      
      for (var url in urls) {
        try {
          response = await http.post(
            Uri.parse(url),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'prompt': _controller.text}),
          ).timeout(Duration(seconds: 45));
          if (response.statusCode == 200) break;
        } catch (e) {
          print("Failed with $url: $e");
          continue;
        }
      }

      if (response != null && response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _image = base64Decode(data['image']);
        });
      } else {
        // Show error
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: Text('Error', style: TextStyle(color: Color(0xFFcf8bfc))),
            backgroundColor: Color(0xFF1a1a1a),
            content: Text('Could not connect to server', style: TextStyle(color: Colors.white70)),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text('OK', style: TextStyle(color: Color(0xFFcf8bfc))),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      print('Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'AI Image Generator',
          style: Theme.of(context).textTheme.displayLarge,
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.palette, size: 24),
            onPressed: () {},
            tooltip: 'Style Options',
          ),
        ],
      ),
      body: Stack(
        children: [
          // Background decorative elements
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0xFFcf8bfc).withOpacity(0.05),
              ),
            ),
          ),
          Positioned(
            bottom: -150,
            left: -100,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0xFFcf8bfc).withOpacity(0.03),
              ),
            ),
          ),
          
          // Main content
          SingleChildScrollView(
            padding: EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome text
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Create Stunning Images',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                        height: 1.2,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Describe your vision in English, Kurdish, or Arabic',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
                
                SizedBox(height: 40),
                
                // Input card
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Column(
                      children: [
                        // Input field
                        TextField(
                          controller: _controller,
                          decoration: InputDecoration(
                            labelText: 'Your Prompt',
                            hintText: 'Type your creative description here...',
                            prefixIcon: Icon(Icons.edit, color: Color(0xFFcf8bfc).withOpacity(0.7)),
                            suffixIcon: _controller.text.isNotEmpty
                                ? IconButton(
                                    icon: Icon(Icons.clear, color: Color(0xFFcf8bfc)),
                                    onPressed: () => _controller.clear(),
                                  )
                                : null,
                          ),
                          maxLines: 3,
                          style: TextStyle(color: Colors.white, fontSize: 16),
                        ),
                        
                        SizedBox(height: 20),
                        
                        // Generate button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _loading ? null : _generate,
                            icon: Icon(
                              _loading ? Icons.hourglass_top : Icons.auto_awesome,
                              size: 24,
                            ),
                            label: _loading
                                ? Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      SizedBox(
                                        width: 20,
                                        height: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white,
                                        ),
                                      ),
                                      SizedBox(width: 12),
                                      Text('Creating Magic...'),
                                    ],
                                  )
                                : Text('Generate Image'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                SizedBox(height: 30),
                
                // Loading indicator section
                if (_loading) ...[
                  Column(
                    children: [
                      LinearProgressIndicator(
                        backgroundColor: Color(0xFF1a1a1a),
                        color: Color(0xFFcf8bfc),
                        borderRadius: BorderRadius.circular(10),
                        minHeight: 6,
                      ),
                      SizedBox(height: 20),
                      Text(
                        'Generating your image... (Usually takes 10-30 seconds)',
                        style: Theme.of(context).textTheme.bodyMedium,
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 40),
                    ],
                  ),
                ],
                
                // Image display
                if (_image != null)
                  Container(
                    margin: EdgeInsets.only(top: 20),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Color(0xFFcf8bfc).withOpacity(0.2),
                          blurRadius: 20,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(20),
                      child: Image.memory(
                        _image!,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                
                // Examples section
                if (_image == null && !_loading) ...[
                  SizedBox(height: 30),
                  Text(
                    '✨ Inspiration Examples',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 16),
                  Container(
                    padding: EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Color(0xFF1a1a1a),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: Color(0xFFcf8bfc).withOpacity(0.2),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildExampleTile('🎨 "A magical forest with glowing mushrooms" (English)'),
                        _buildExampleTile('🏔️ "گوڵێکی زەرد لە بناری چیایەک" (Kurdish)'),
                        _buildExampleTile('🐉 "Ancient dragon flying over castle ruins" (English)'),
                      ],
                    ),
                  ),
                ],
                
                // Spacing for footer
                SizedBox(height: 100),
                                  Center(
                                    child: Text(
                                                        'Developed by Zinar Mizury',
                                                        style: TextStyle(
                                                          color: Colors.grey[700],
                                                          fontSize: 12,
                                                         // fontWeight: FontWeight.w600,
                                                        ),
                                                      ),
                                  ),
              ],
            ),
          ),
        ],
      ),
      
      // Footer
      
      

    );
  }

  Widget _buildExampleTile(String text) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: EdgeInsets.only(top: 6, right: 12),
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Color(0xFFcf8bfc),
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: Colors.white70,
                fontSize: 15,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}