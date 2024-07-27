# from django.test import TestCase
# from accounts.models import User
# from quote.models import Quote, Tag
# from quote.serializers import QuoteSerializer

# class QuoteSerializerTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='testuser@example.com', password='testpass', nickname='test', name='Test User', age=30, sex='male', birth='1993-01-01', phone='010-1234-5678')
#         self.tag = Tag.objects.create(name='inspirational')

#     def test_create_quote_updates_duplicate_quotes(self):
#         data = {
#             'content': 'Test Quote',
#             'description': 'This is a test quote.',
#             'author': 'Test Author',
#             'registrant': self.user.id,
#             'tag': ['inspirational']
#         }
#         serializer = QuoteSerializer(data=data)
#         if serializer.is_valid():
#             quote = serializer.save()
#             self.user.refresh_from_db()  # DB로부터 user 정보를 다시 로드하여 최신 상태 반영
#             self.assertIn(quote.id, self.user.duplicate_quotes)
        
#         # 동일한 명언을 다시 생성할 수 없어야 합니다.
#         serializer = QuoteSerializer(data=data)
#         if serializer.is_valid():
#             quote = serializer.save()
#             self.user.refresh_from_db()
#             self.assertEqual(self.user.duplicate_quotes.count(quote.id), 1)
