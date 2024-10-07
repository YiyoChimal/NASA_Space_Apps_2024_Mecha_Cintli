import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

class SplashPage extends StatelessWidget {
   SplashPage({super.key});
  final btnStyle = ElevatedButton.styleFrom(
    elevation: 8,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(30),
    ),
    backgroundColor: const Color.fromRGBO(231, 246, 212, 0.43),
    foregroundColor: Colors.black,
    minimumSize: const Size(250, 50), 
    textStyle: TextStyle(
      fontFamily: GoogleFonts.firaSans().fontFamily,
      fontWeight: FontWeight.bold,
      color: const Color.fromRGBO(27, 51, 34, 1),
      fontSize: 20,
    ),
  );

  @override
  Widget build(BuildContext context) {
    return  Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/splash_top.png'),
            fit: BoxFit.cover,
          ),
        ),
        child:  Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Crop Shield',
                style: TextStyle(
                  fontSize: 45,
                  fontWeight: FontWeight.bold,
                  color: Color.fromRGBO(27, 51, 34, 1),
                ),
              ),
              ElevatedButton(onPressed: () => context.go('/login'),style: btnStyle, child: const Text('Login'),),
              const SizedBox(height: 20),
              ElevatedButton(onPressed: () => context.go('/sign_up'),style: btnStyle, child: const Text('Sign Up'),)
            ],
          ),
        ),
      ),
    );
  }
}