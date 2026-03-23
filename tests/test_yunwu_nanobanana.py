import unittest

from app.services.media_generation import media_generation_registry
from app.services.nanobanana.yunwu import NanoBananaYunwu


class NanoBananaYunwuTests(unittest.TestCase):
    def setUp(self):
        self.service = NanoBananaYunwu("test-key")

    def test_collect_ref_images_supports_batch_and_legacy_inputs(self):
        result = self.service._collect_ref_images(
            {
                "ref_images": [{"base64": "AAA", "mime": "image/png"}],
                "ref_image": "BBB",
                "ref_mime_type": "image/jpeg",
            }
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["mime"], "image/png")
        self.assertEqual(result[1]["base64"], "BBB")
        self.assertEqual(result[1]["mime"], "image/jpeg")

    def test_normalize_queue_url_rewrites_fal_queue_domain(self):
        normalized = self.service._normalize_queue_url(
            "https://queue.fal.run/fal-ai/nano-banana/requests/abc/status"
        )
        self.assertEqual(
            normalized,
            "https://yunwu.ai/fal-ai/nano-banana/requests/abc/status",
        )

    def test_extract_image_url_supports_nested_images_payload(self):
        image_url = self.service._extract_image_url(
            {
                "images": [
                    {
                        "url": "https://example.com/result.png",
                    }
                ]
            }
        )
        self.assertEqual(image_url, "https://example.com/result.png")

    def test_extract_error_message_supports_multiple_shapes(self):
        self.assertEqual(
            self.service._extract_error_message({"error": {"message": "bad request"}}),
            "bad request",
        )
        self.assertEqual(
            self.service._extract_error_message({"message": "plain error"}),
            "plain error",
        )


class MediaGenerationRegistryTests(unittest.TestCase):
    def test_yunwu_generator_is_registered(self):
        generator = media_generation_registry.get_image_generator("nanobanana", "yunwu")
        self.assertIsNotNone(generator)
        self.assertEqual(generator.provider, "yunwu")
        self.assertEqual(generator.platform, "nanobanana")


if __name__ == "__main__":
    unittest.main()
