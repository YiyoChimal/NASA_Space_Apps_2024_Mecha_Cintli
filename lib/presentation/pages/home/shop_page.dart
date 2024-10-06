import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../widgets/seach_widget.dart';

class ShopPage extends StatelessWidget {
  const ShopPage({super.key});

  final greenAccent = const Color.fromRGBO(146, 172, 143, 0.41);
  final primaryGreen = const Color.fromRGBO(88, 144, 107, 1);
  final secondaryGreen = const Color.fromRGBO(146, 172, 143, 0.41);
  final hintColor = const Color.fromRGBO(121, 121, 121, 1);
  final backgroundColor = const Color.fromRGBO(255, 255, 255, 1);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: ListView(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Shop',
                    style: GoogleFonts.firaSans(
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        color: hintColor),
                  ),
                  IconButton(
                      onPressed: () {}, icon: const Icon(Icons.notifications))
                ],
              ),
              const SizedBox(height: 20),
              homeTextInput(),
              const SizedBox(height: 20),
              const Text('What are we selling?',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  )),
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerRight,
                child: Container(
                  width: MediaQuery.of(context).size.width * 0.5,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      color: greenAccent),
                  child: const Text(
                      'For those interested in taking care of the soil, we created something new that you may desire in your farm. We call this the smart rod, capable of measuring multiple factors, such as humidity, pressure, ph, temperature and more!'),
                ),
              ),
              const SizedBox(height: 20),
              Align(
                alignment: Alignment.centerLeft,
                child: Container(
                  width: double.infinity,
                  height: 300,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      color: greenAccent),
                  child: const Text(
                      'In order to send all the data, you need the second part of our invention, which is included within the smart rod. This device has the mission of reading all the data outside and far from your setup. After that, the information is uploaded to this app'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
