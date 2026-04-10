import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/features/auth/data/auth_models.dart';

void main() {
  group('User', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'user-1',
        'name': 'Salman Ahmed',
        'email': 'salman@example.com',
        'profile_picture': 'https://cdn.example.com/avatar.jpg',
        'bio': 'Software Engineer',
        'phone_number': '+967776071221',
      };
      final user = User.fromJson(json);

      expect(user.id, 'user-1');
      expect(user.name, 'Salman Ahmed');
      expect(user.email, 'salman@example.com');
      expect(user.avatarUrl, 'https://cdn.example.com/avatar.jpg');
      expect(user.bio, 'Software Engineer');
      expect(user.phoneNumber, '+967776071221');
    });

    test('fromJson uses full_name fallback', () {
      // Backend sends 'full_name' in some endpoints
      final json = {'id': 'user-2', 'full_name': 'Mohammed Ali', 'email': 'mo@test.com'};
      final user = User.fromJson(json);

      expect(user.name, 'Mohammed Ali');
    });

    test('fromJson handles null optional fields', () {
      final json = {'id': 'user-3', 'name': 'Test', 'email': 'test@test.com'};
      final user = User.fromJson(json);

      expect(user.avatarUrl, isNull);
      expect(user.bio, isNull);
      expect(user.phoneNumber, isNull);
    });
  });

  group('AuthResponse', () {
    test('fromJson parses tokens and user', () {
      final json = {
        'access_token': 'eyJhbGciOi...',
        'refresh_token': 'eyJhbGciOi_refresh...',
        'user': {
          'id': 'u1',
          'name': 'Test User',
          'email': 'test@viora.app',
        },
      };
      final response = AuthResponse.fromJson(json);

      expect(response.accessToken, 'eyJhbGciOi...');
      expect(response.refreshToken, 'eyJhbGciOi_refresh...');
      expect(response.user.id, 'u1');
      expect(response.user.name, 'Test User');
      expect(response.user.email, 'test@viora.app');
    });
  });
}
