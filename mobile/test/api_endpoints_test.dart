import 'package:flutter_test/flutter_test.dart';
import 'package:viora_app/core/api/api_endpoints.dart';

void main() {
  group('Endpoints', () {
    group('Auth endpoints', () {
      test('register path', () => expect(Endpoints.register, '/api/auth/register'));
      test('login path', () => expect(Endpoints.login, '/api/auth/login'));
      test('refresh path', () => expect(Endpoints.refresh, '/api/auth/refresh'));
    });

    group('Resume endpoints', () {
      test('upload path', () => expect(Endpoints.resumeUpload, '/api/resume/upload'));
      test('analyze path', () => expect(Endpoints.resumeAnalyze, '/api/resume/analyze'));
      test('analyze stream path', () => expect(Endpoints.resumeAnalyzeStream, '/api/resume/analyze/stream'));
    });

    group('Dashboard endpoint', () {
      test('dashboard path', () => expect(Endpoints.dashboard, '/api/dashboard'));
    });

    group('Roadmap endpoints', () {
      test('roadmap base', () => expect(Endpoints.roadmap, '/api/roadmap'));
      test('generate', () => expect(Endpoints.roadmapGenerate, '/api/roadmap/generate'));
      test('step complete (index 0)', () => expect(Endpoints.roadmapStepComplete(0), '/api/roadmap/steps/0/complete'));
      test('step complete (index 5)', () => expect(Endpoints.roadmapStepComplete(5), '/api/roadmap/steps/5/complete'));
      test('step incomplete (index 2)', () => expect(Endpoints.roadmapStepIncomplete(2), '/api/roadmap/steps/2/incomplete'));
    });

    group('Chat endpoints', () {
      test('send', () => expect(Endpoints.chatSend, '/api/chat/send'));
      test('history', () => expect(Endpoints.chatHistory, '/api/chat/history'));
    });

    group('Profile endpoints', () {
      test('profile', () => expect(Endpoints.profile, '/api/profile'));
      test('avatar', () => expect(Endpoints.profileAvatar, '/api/profile/avatar'));
      test('language', () => expect(Endpoints.language, '/api/profile/settings/language'));
    });

    group('Notifications endpoints', () {
      test('notifications list', () => expect(Endpoints.notifications, '/api/notifications'));
      test('mark read (id)', () => expect(Endpoints.notificationRead('abc'), '/api/notifications/abc/read'));
    });

    // Progress endpoint not yet implemented in backend
    // group('Progress endpoints', () {
    //   test('weekly activity', () => expect(Endpoints.weeklyActivity, '/api/progress/weekly'));
    // });

    group('Courses endpoints', () {
      test('courses list', () => expect(Endpoints.courses, '/api/courses'));
      test('single course', () => expect(Endpoints.course('c1'), '/api/courses/c1'));
    });
  });
}
