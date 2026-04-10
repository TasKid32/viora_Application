import 'package:dio/dio.dart';
import '../utils/logger.dart';

/// Quota interceptor — handles 403/429 rate limit errors gracefully.
///
/// Shows user-friendly error messages for quota/rate-limit errors.
class QuotaInterceptor extends Interceptor {
  static const _tag = 'Quota';

  /// Optional callback for showing SnackBars or dialogs.
  final void Function(String message)? onQuotaError;

  QuotaInterceptor({this.onQuotaError});

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final status = err.response?.statusCode;

    if (status == 429) {
      Log.w(_tag, 'Rate limit exceeded (429)');
      final message = _extractMessage(err) ?? 'Too many requests. Please wait a moment.';
      onQuotaError?.call(message);

      // Replace error with user-friendly message
      handler.reject(DioException(
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        error: message,
        message: message,
      ));
      return;
    }

    if (status == 403) {
      final data = err.response?.data;
      final isQuota = data is Map && (
        data.containsKey('quota') ||
        (data['detail']?.toString().toLowerCase().contains('quota') ?? false) ||
        (data['detail']?.toString().toLowerCase().contains('limit') ?? false)
      );

      if (isQuota) {
        Log.w(_tag, 'Quota exceeded (403)');
        final message = _extractMessage(err) ?? 'API quota exceeded. Please try again later.';
        onQuotaError?.call(message);
      }
    }

    super.onError(err, handler);
  }

  String? _extractMessage(DioException err) {
    final data = err.response?.data;
    if (data is Map && data.containsKey('detail')) {
      return data['detail']?.toString();
    }
    return null;
  }
}
