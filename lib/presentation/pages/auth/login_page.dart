
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

class LoginPage extends StatelessWidget {
  LoginPage({super.key});
  final backgroundColor = const Color.fromRGBO(143, 113, 85, 0.79);
  final greenAccent = const Color.fromARGB(231, 185, 222, 181);
  final titleStyle = TextStyle(
    fontFamily: GoogleFonts.aDLaMDisplay().fontFamily,
    fontSize: 45,
    fontWeight: FontWeight.bold,
    color: const Color.fromRGBO(27, 51, 34, 1),
  );

  

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
          backgroundColor: backgroundColor,
          body: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Stack(
                children: [
                  Container(
                    width: double.infinity,
                    height: 250,
                    decoration: const BoxDecoration(
                      image: DecorationImage(
                        image: AssetImage('assets/images/splash_top.png'),
                        fit: BoxFit.cover,
                      ),
                      borderRadius: BorderRadius.only(
                        bottomLeft: Radius.circular(150),
                        bottomRight: Radius.circular(150),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 90),
              Text(
                'Login',
                style: titleStyle,
              ),
              const SizedBox(height: 20),
              signUpTextField('Username', Icons.account_circle),
              signUpTextField('Password', Icons.lock),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: () => context.go('/'), // Navegar a la ruta '/'
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      backgroundColor: const Color.fromRGBO(168, 133, 84, 1),
                      foregroundColor: Colors.black,
                      textStyle: TextStyle(
                        fontFamily: GoogleFonts.flamenco().fontFamily,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    child: const Text('Cancel'),
                  ),
                  ElevatedButton(
                    onPressed: () => context.push('/main'),
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      backgroundColor: const Color.fromRGBO(168, 133, 84, 1),
                      foregroundColor: Colors.black,
                      textStyle: TextStyle(
                        fontFamily: GoogleFonts.flamenco().fontFamily,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    child: const Text('Submit'),
                  ),
                ],
              ),
              const Spacer(),
              Expanded(
                child: Stack(
                  clipBehavior: Clip.none,
                  children: [
                    Positioned(
                      top: 0,
                      left: -100,
                      child: CircleAvatar(
                        radius: 150,
                        backgroundColor: Colors.green[800],
                      ),
                    ),
                    Positioned(
                      bottom: -170,
                      right: -100,
                      child: CircleAvatar(
                        radius: 160,
                        backgroundColor: Colors.green[400],
                      ),
                    ),
                    Positioned(
                      bottom: -120,
                      left: 110,
                      child: CircleAvatar(
                        radius: 80,
                        backgroundColor: Colors.green[200],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Positioned(
          left: MediaQuery.of(context).size.width / 2 - 70,
          top: 200,
          child: const CircleAvatar(
            radius: 70,
            backgroundImage: AssetImage('assets/images/Logo.png'),
          ),
        ),
      ],
    );
  }

  Container signUpTextField(String hintText, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 50),
      margin: const EdgeInsets.symmetric(vertical: 10),
      child: TextField(
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(
            fontFamily: GoogleFonts.flamenco().fontFamily,
            fontWeight: FontWeight.bold,
          ),
          prefixIcon: Icon(icon),
          filled: true,
          fillColor: greenAccent,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
          ),
        ),
      ),
    );
  }
}
