import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:viora_app/core/utils/error_helper.dart';

void main() {
  group('extractDioError', () {
    test('extracts detail from Backend response', () {
      final e = DioException(
        requestOptions: RequestOptions(path: '/api/auth/login'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/auth/login'),
          statusCode: 400,
          data: {'detail': 'Invalid email or password'},
        ),
      );

      expect(extractDioError(e), 'Invalid email or password');
    });

    test('returns connection timeout message', () {
      final e = DioException(
        type: DioExceptionType.connectionTimeout,
        requestOptions: RequestOptions(path: '/api/dashboard'),
      );

      expect(extractDioError(e), 'Connection timed out — check your network');
    });

    test('returns connection error message', () {
      final e = DioException(
        type: DioExceptionType.connectionError,
        requestOptions: RequestOptions(path: '/api/dashboard'),
      );

      expect(extractDioError(e), 'Could not connect to server');
    });

    test('returns generic message for unknown errors', () {
      final e = DioException(
        type: DioExceptionType.unknown,
        requestOptions: RequestOptions(path: '/api/test'),
      );

      expect(extractDioError(e), 'An error occurred — please try again');
    });

    test('handles non-Map response data', () {
      final e = DioException(
        requestOptions: RequestOptions(path: '/api/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/test'),
          statusCode: 500,
          data: 'Internal Server Error', // String, not Map
        ),
      );

      expect(extractDioError(e), 'An error occurred — please try again');
    });

    test('handles response without detail key', () {
      final e = DioException(
        requestOptions: RequestOptions(path: '/api/test'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/test'),
          statusCode: 422,
          data: {'error': 'Validation failed', 'fields': ['email']}, // No 'detail'
        ),
      );

      expect(extractDioError(e), 'An error occurred — please try again');
    });

    test('handles quota error (429)', () {
      final e = DioException(
        requestOptions: RequestOptions(path: '/api/resume/analyze'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/resume/analyze'),
          statusCode: 429,
          data: {'detail': 'Rate limit exceeded. Try again in 60 seconds.'},
        ),
      );

      expect(extractDioError(e), 'Rate limit exceeded. Try again in 60 seconds.');
    });
  });
}
