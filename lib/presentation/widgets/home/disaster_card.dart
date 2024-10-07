import 'package:flutter/material.dart';

class DisasterCard extends StatelessWidget {
  const DisasterCard({super.key, required this.title, required this.path});

  final String title;
  final String path;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 170,
      margin: const EdgeInsets.only(right: 5),
      child: Card(
        color: const Color.fromRGBO(71, 133, 92, 0.91),
        child: Column(
          children: [
             Image(
              image: AssetImage(path),
            ),
            Container(
                decoration: BoxDecoration(
                  color: const Color.fromRGBO(44, 88, 59, 1.91),
                  borderRadius: BorderRadius.circular(5),
                ),
                child:  Text(title)),
          ],
        ),
      ),
    );
  }
}
