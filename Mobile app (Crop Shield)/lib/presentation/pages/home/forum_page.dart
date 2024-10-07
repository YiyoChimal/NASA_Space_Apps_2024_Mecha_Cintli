import 'package:crop_shield/presentation/widgets/forum_tile.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../widgets/seach_widget.dart';

class ForumPage extends StatefulWidget {
  const ForumPage({super.key});

  @override
  State<ForumPage> createState() => _ForumPageState();
}

class _ForumPageState extends State<ForumPage> {
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
                    'Forum',
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
              const ForumTile(),
              const ForumTile(),
              const ForumTile(),
              const ForumTile(),
            ],
          ),
        ),
      ),
    );
  }
}
