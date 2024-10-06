import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

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
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Profile',
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
              const CircleAvatar(
                radius: 90,
                backgroundImage: AssetImage('assets/images/profile.png'),
              ),
              const SizedBox(height: 50),
              const Text('sada_08200336',
                  style: TextStyle(
                    fontSize: 25,
                    fontWeight: FontWeight.bold,
                  )),
              const SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 50),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    TextButton(
                      onPressed: () {},
                      style: const ButtonStyle(
                        foregroundColor: WidgetStatePropertyAll(Colors.black),
                        padding:
                            WidgetStatePropertyAll(EdgeInsets.only(left: 20)),
                      ),
                      child: const Text('25 followers'),
                    ),
                    const Text(
                      '|',
                    ),
                    TextButton(
                      onPressed: () {},
                      style: const ButtonStyle(
                        foregroundColor: WidgetStatePropertyAll(Colors.black),
                        padding:
                            WidgetStatePropertyAll(EdgeInsets.only(right: 20)),
                      ),
                      child: const Text('3 following'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {},
                style: ButtonStyle(
                  minimumSize: const WidgetStatePropertyAll(Size(200, 50)),
                  backgroundColor: WidgetStatePropertyAll(secondaryGreen),
                ),
                child: const Text(
                  'Edit Profile',
                  style: TextStyle(
                    fontWeight: FontWeight.w500,
                    color: Colors.black,
                  ),
                ),
              ),
              const SizedBox(height: 40),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconCircleButton(
                    icon: Icons.share,
                    text: 'Share',
                  ),
                  IconCircleButton(
                    icon: Icons.edit,
                    text: 'Created',
                  ),
                  IconCircleButton(
                    icon: Icons.bookmark,
                    text: 'Saved',
                  )
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}

class IconCircleButton extends StatelessWidget {
  const IconCircleButton({
    super.key,
    required this.icon,
    required this.text,
  });

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color.fromRGBO(217, 217, 217, 1),
            borderRadius: BorderRadius.circular(50),
          ),
          child: IconButton(onPressed: () {}, icon: Icon(icon,size: 35,)),
        ),
        const SizedBox(height: 5),
        Text(text),
      ],
    );
  }
}
