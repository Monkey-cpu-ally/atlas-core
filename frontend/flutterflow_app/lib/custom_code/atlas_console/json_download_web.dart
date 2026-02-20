import 'dart:html' as html;

Future<bool> downloadJsonFile({
  required String fileName,
  required String jsonPayload,
}) async {
  final blob = html.Blob(
    <Object>[jsonPayload],
    'application/json;charset=utf-8',
  );
  final url = html.Url.createObjectUrlFromBlob(blob);
  final anchor = html.AnchorElement(href: url)
    ..download = fileName
    ..style.display = 'none';
  html.document.body?.append(anchor);
  anchor.click();
  anchor.remove();
  html.Url.revokeObjectUrl(url);
  return true;
}
