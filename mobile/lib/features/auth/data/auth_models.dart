/// User model — matches Backend auth response.
class User {
  final String id;
  final String name;
  final String email;
  final String? avatarUrl;
  final String? bio;
  final String? phoneNumber;

  const User({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    this.bio,
    this.phoneNumber,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      name: (json['name'] ?? json['full_name']) as String,
      email: json['email'] as String,
      avatarUrl: json['profile_picture'] as String?,
      bio: json['bio'] as String?,
      phoneNumber: json['phone_number'] as String?,
    );
  }
}

/// Auth response — tokens + user.
class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final User user;

  const AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}
