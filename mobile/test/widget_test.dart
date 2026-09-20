import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aurora_store_mobile/widgets/aurora_button.dart';
import 'package:aurora_store_mobile/widgets/aurora_badge.dart';

void main() {
  testWidgets('Aurora widgets smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Column(
            children: [
              AuroraButton(text: 'Pagar Ahora', onPressed: null),
              AuroraBadge(text: 'PAGADO'),
            ],
          ),
        ),
      ),
    );

    expect(find.text('Pagar Ahora'), findsOneWidget);
    expect(find.text('PAGADO'), findsOneWidget);
  });
}
