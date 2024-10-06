import 'package:crop_shield/presentation/pages/home_page.dart';
import 'package:crop_shield/presentation/pages/login_page.dart';
import 'package:crop_shield/presentation/pages/sign_up.page.dart';
import 'package:go_router/go_router.dart';

final GoRouter router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (context, state) =>  SignUpPage(),),
    GoRoute(path: '/login', builder: (context, state) =>  LoginPage(),),
    GoRoute(path: '/home', builder: (context, state) => const HomePage(),),
  ]
);
    