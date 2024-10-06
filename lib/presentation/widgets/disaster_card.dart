import 'package:flutter/material.dart';

class DisasterCard extends StatelessWidget {
  const DisasterCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 150,
      padding: const EdgeInsets.all(10),
      child: Card(
        color: const Color.fromRGBO(71, 133, 92, 0.91),
        child: Column(
          children: [
            const Image(
              image: AssetImage('assets/images/flood.png'),
            ),
            Container(
                decoration: BoxDecoration(
                  color: const Color.fromRGBO(44, 88, 59, 1.91),
                  borderRadius: BorderRadius.circular(5),
                ),
                child: const Text('Droughts'))
          ],
        ),
      ),
    );
  }
}
