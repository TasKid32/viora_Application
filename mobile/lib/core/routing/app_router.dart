import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/auth/screens/forgot_password_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/analysis/screens/analysis_screen.dart';
import '../../features/roadmap/screens/roadmap_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/notifications/screens/notifications_screen.dart';
import '../../features/chat/widgets/chat_bottom_sheet.dart';
import '../../core/theme/app_colors.dart';

/// Named route paths.
class Routes {
  Routes._();

  static const String login = '/login';
  static const String register = '/register';
  static const String home = '/';
  static const String analysis = '/analysis';
  static const String roadmap = '/roadmap';
  static const String profile = '/profile';
  static const String notifications = '/notifications';
  static const String forgotPassword = '/forgot-password';
}

/// Auth state notifier — GoRouter listens to this and re-evaluates redirects.
/// This is a lightweight ChangeNotifier, NOT the full AuthProvider.
class AuthStateNotifier extends ChangeNotifier {
  bool _isAuthenticated;

  AuthStateNotifier(this._isAuthenticated);

  bool get isAuthenticated => _isAuthenticated;

  set isAuthenticated(bool value) {
    if (_isAuthenticated != value) {
      _isAuthenticated = value;
      notifyListeners(); // triggers GoRouter.redirect re-evaluation
    }
  }
}

/// Creates a SINGLETON GoRouter — called ONCE, not on every build.
///
/// Uses [refreshListenable] to re-evaluate [redirect] when auth state changes,
/// WITHOUT recreating the entire router (preserves navigation stack!).
GoRouter createRouter({required AuthStateNotifier authNotifier}) {
  return GoRouter(
    initialLocation: Routes.login,
    refreshListenable: authNotifier,
    routes: [
      // Auth routes (no bottom nav)
      GoRoute(path: Routes.login, builder: (_, __) => const LoginScreen()),
      GoRoute(
          path: Routes.register, builder: (_, __) => const RegisterScreen()),
      GoRoute(
          path: Routes.forgotPassword,
          builder: (_, __) => const ForgotPasswordScreen()),

      // Full-screen push routes (no bottom nav)
      GoRoute(
          path: Routes.notifications,
          builder: (_, __) => const NotificationsScreen()),

      // Main app with bottom navigation + FAB chat
      ShellRoute(
        builder: (_, state, child) => _MainShell(child: child),
        routes: [
          GoRoute(
              path: Routes.home, builder: (_, __) => const DashboardScreen()),
          GoRoute(
              path: Routes.analysis,
              builder: (_, __) => const AnalysisScreen()),
          GoRoute(
              path: Routes.roadmap, builder: (_, __) => const RoadmapScreen()),
          GoRoute(
              path: Routes.profile, builder: (_, __) => const ProfileScreen()),
        ],
      ),
    ],
    redirect: (context, state) {
      final isAuth = authNotifier.isAuthenticated;
      final loc = state.matchedLocation;

      final isAuthRoute = loc == Routes.login ||
          loc == Routes.register ||
          loc == Routes.forgotPassword;
      if (!isAuth && !isAuthRoute) return Routes.login;
      if (isAuth && isAuthRoute) return Routes.home;
      return null;
    },
  );
}

/// Main shell with bottom navigation bar + floating chat FAB.
class _MainShell extends StatelessWidget {
  final Widget child;
  const _MainShell({required this.child});

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    switch (location) {
      case Routes.home:
        return 0;
      case Routes.analysis:
        return 1;
      case Routes.roadmap:
        return 2;
      case Routes.profile:
        return 3;
      default:
        return 0;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      // Simple FAB — clean, no gradient wrapper
      floatingActionButton: FloatingActionButton(
        onPressed: () => showChatBottomSheet(context),
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.white,
        elevation: 2,
        child: const Icon(Icons.smart_toy_outlined, size: 24),
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: AppColors.outlineVariant, width: 1),
          ),
        ),
        child: NavigationBar(
          selectedIndex: _currentIndex(context),
          onDestinationSelected: (i) {
            switch (i) {
              case 0:
                context.go(Routes.home);
              case 1:
                context.go(Routes.analysis);
              case 2:
                context.go(Routes.roadmap);
              case 3:
                context.go(Routes.profile);
            }
          },
          destinations: [
            NavigationDestination(
                icon: const Icon(Icons.home_outlined),
                selectedIcon: const Icon(Icons.home),
                label: AppLocalizations.of(context)!.navHome),
            NavigationDestination(
                icon: const Icon(Icons.analytics_outlined),
                selectedIcon: const Icon(Icons.analytics),
                label: AppLocalizations.of(context)!.navAnalysis),
            NavigationDestination(
                icon: const Icon(Icons.map_outlined),
                selectedIcon: const Icon(Icons.map),
                label: AppLocalizations.of(context)!.navRoadmap),
            NavigationDestination(
                icon: const Icon(Icons.person_outline),
                selectedIcon: const Icon(Icons.person),
                label: AppLocalizations.of(context)!.navProfile),
          ],
        ),
      ),
    );
  }
}
