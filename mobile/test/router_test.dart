import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/core/routing/app_router.dart';

void main() {
  group('Routes', () {
    test('all route paths are correct', () {
      expect(Routes.login, '/login');
      expect(Routes.register, '/register');
      expect(Routes.home, '/');
      expect(Routes.analysis, '/analysis');
      expect(Routes.roadmap, '/roadmap');
      expect(Routes.profile, '/profile');
      expect(Routes.notifications, '/notifications');
    });
  });

  group('AuthStateNotifier', () {
    test('initial state matches constructor', () {
      final notifier = AuthStateNotifier(false);
      expect(notifier.isAuthenticated, false);

      final notifier2 = AuthStateNotifier(true);
      expect(notifier2.isAuthenticated, true);
    });

    test('setting same value does not notify', () {
      final notifier = AuthStateNotifier(true);
      int notifyCount = 0;
      notifier.addListener(() => notifyCount++);

      notifier.isAuthenticated = true; // Same value
      expect(notifyCount, 0);
    });

    test('setting different value notifies listeners', () {
      final notifier = AuthStateNotifier(true);
      int notifyCount = 0;
      notifier.addListener(() => notifyCount++);

      notifier.isAuthenticated = false; // Changed
      expect(notifyCount, 1);
      expect(notifier.isAuthenticated, false);
    });

    test('multiple state changes notify correctly', () {
      final notifier = AuthStateNotifier(false);
      final states = <bool>[];
      notifier.addListener(() => states.add(notifier.isAuthenticated));

      notifier.isAuthenticated = true;  // Changed
      notifier.isAuthenticated = true;  // Same — no notify
      notifier.isAuthenticated = false; // Changed
      notifier.isAuthenticated = false; // Same — no notify

      expect(states, [true, false]);
    });
  });
}
