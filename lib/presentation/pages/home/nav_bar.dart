import 'package:crop_shield/presentation/pages/home/home_page.dart';
import 'package:flutter/material.dart';
import 'package:persistent_bottom_nav_bar/persistent_bottom_nav_bar.dart';

class MainHome extends StatefulWidget {
  const MainHome({super.key});

  @override
  State<MainHome> createState() => _MainHomeState();
}

List<Widget> _buildScreens() {
  return [
    const HomePage(),
    const Center(child: Text('Forum')),
    const Center(child: Text('Map')),
    const Center(child: Text('Market')),
    const Center(child: Text('Profile')),
  ];
}

List<PersistentBottomNavBarItem> _navBarsItems() {
  return [
    PersistentBottomNavBarItem(
      icon: const Icon(Icons.home),
      title: ("Home"),
      activeColorPrimary: Colors.green,
      inactiveColorPrimary: Colors.grey,
    ),
    PersistentBottomNavBarItem(
      icon: const Icon(Icons.forum),
      title: ("Forum"),
      activeColorPrimary: Colors.green,
      inactiveColorPrimary: Colors.grey,
    ),
    PersistentBottomNavBarItem(
      icon: const Icon(Icons.map_outlined),
      title: ("Map"),
      activeColorPrimary: Colors.green,
      inactiveColorPrimary: Colors.grey,
    ),
    PersistentBottomNavBarItem(
      icon: const Icon(Icons.shopping_cart),
      title: ("Market"),
      activeColorPrimary: Colors.green,
      inactiveColorPrimary: Colors.grey,
    ),
    PersistentBottomNavBarItem(
      icon: const Icon(Icons.person),
      title: ("Profile"),
      activeColorPrimary: Colors.green,
      inactiveColorPrimary: Colors.grey,
    ),
  ];
}

class _MainHomeState extends State<MainHome> {
  final PersistentTabController _controller = PersistentTabController(initialIndex: 0);

  @override
  Widget build(BuildContext context) {
    return PersistentTabView(
      context,
      controller: _controller,
      screens: _buildScreens(),
      items: _navBarsItems(),
      navBarStyle: NavBarStyle.style15, 
    );
  }
}