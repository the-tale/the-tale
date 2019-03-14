
import smart_imports

smart_imports.all()


class TestCaseMixin(object):

    def check_protobuf_ok(self, response, answer_type, content_type='application/protobuf'):
        self.assertTrue(content_type in response['Content-Type'])

        self.assertEqual(response.status_code, 200)

        return answer_type.FromString(response.content)

    def post_protobuf(self, url, data=None):
        return self.client.post(url,
                                data if data else '',
                                HTTP_ACCEPT='text/json',
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                content_type='application/protobuf')
