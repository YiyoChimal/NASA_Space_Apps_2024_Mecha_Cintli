import 'package:flutter/material.dart';

class LoginPage extends StatelessWidget {
   LoginPage({super.key});
 final backgroundColor = Color(0x8F7155C9);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor ,
      body: Column(
        children: [
          Container(
            width: double.infinity,
            height: 400,
            decoration: const BoxDecoration(
                image: DecorationImage(
                    image: AssetImage('assets/images/splash_top.png'),
                    fit: BoxFit.cover)),
          ),
        ],
      ),
    );
  }
}