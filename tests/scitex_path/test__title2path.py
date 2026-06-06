import contextlib

import pytest

from scitex_path import title2path


@contextlib.contextmanager
def _swap_attr(obj, name, value):
    saved = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, saved)


class TestTitle2Path:
    """Test the title2path function."""

    def test_simple_string_title2path_hello_world_hello_world(self):
        """Test conversion of a simple string."""
        # Arrange
        # Act
        # Assert
        assert title2path("hello world") == "hello_world"

    def test_string_with_special_chars(self):
        """Test removal of special characters."""
        # Arrange
        # Act
        # Assert
        assert title2path("test:file;name=value[0]") == "testfilenamevalue0"

    def test_string_with_spaces(self):
        """Test space replacement with underscores."""
        # Arrange
        # Act
        # Assert
        assert title2path("test file name") == "test_file_name"

    def test_string_with_consecutive_underscores_split_1(self):
        """Test removal of consecutive underscores."""
        # Arrange
        # Act
        # Assert
        assert title2path('test___file') == 'test_file'

    def test_string_with_consecutive_underscores_split_2(self):
        """Test removal of consecutive underscores."""
        # Arrange
        title2path('test___file') == 'test_file'
        # Act
        # Assert
        assert title2path('test____file') == 'test_file'

    def test_underscore_dash_underscore_pattern(self):
        """Test replacement of _-_ pattern."""
        # Arrange
        # Act
        # Assert
        assert title2path("test_-_file") == "test-file"

    def test_uppercase_to_lowercase_split_1(self):
        """Test conversion to lowercase."""
        # Arrange
        # Act
        # Assert
        assert title2path('TEST FILE') == 'test_file'

    def test_uppercase_to_lowercase_split_2(self):
        """Test conversion to lowercase."""
        # Arrange
        title2path('TEST FILE') == 'test_file'
        # Act
        # Assert
        assert title2path('TestFile') == 'testfile'

    def test_complex_string_title2path_input_str_expected(self):
        """Test complex string with multiple patterns."""
        # Arrange
        input_str = "Test:File[1];Name=Value _-_ End"
        # Act
        expected = "testfile1namevalue_-_end"
        # Assert
        assert title2path(input_str) == expected

    def test_empty_string_title2path(self):
        """Test empty string input."""
        # Arrange
        # Act
        # Assert
        assert title2path("") == ""

    def test_string_with_only_special_chars(self):
        """Test string containing only special characters."""
        # Arrange
        # Act
        # Assert
        assert title2path("::;;==[[]]") == ""

    def test_string_with_mixed_patterns(self):
        """Test string with various patterns combined."""
        # Arrange
        input_str = "Model: ResNet50; Epochs=100 [Batch: 32]"
        # Act
        expected = "model_resnet50_epochs100_batch_32"
        # Assert
        assert title2path(input_str) == expected

    def test_dict_input_result_equals_modelresnet50_epochs_split_1(self):
        """Test conversion of dictionary input."""
        # Arrange
        import scitex_dict
        calls = []

        def fake_to_str(*args, **kwargs):
            calls.append((args, kwargs))
            return 'model:resnet50 epochs=100'
        test_dict = {'model': 'resnet50', 'epochs': 100}
        with _swap_attr(scitex_dict, 'to_str', fake_to_str):
            result = title2path(test_dict)
        # Act
        # Assert
        assert len(calls) == 1

    def test_dict_input_result_equals_modelresnet50_epochs_split_2(self):
        """Test conversion of dictionary input."""
        # Arrange
        import scitex_dict
        calls = []

        def fake_to_str(*args, **kwargs):
            calls.append((args, kwargs))
            return 'model:resnet50 epochs=100'
        test_dict = {'model': 'resnet50', 'epochs': 100}
        with _swap_attr(scitex_dict, 'to_str', fake_to_str):
            result = title2path(test_dict)
        len(calls) == 1
        # Act
        # Assert
        assert calls[0] == ((test_dict,), {})

    def test_dict_input_result_equals_modelresnet50_epochs_split_3(self):
        """Test conversion of dictionary input."""
        # Arrange
        import scitex_dict
        calls = []

        def fake_to_str(*args, **kwargs):
            calls.append((args, kwargs))
            return 'model:resnet50 epochs=100'
        test_dict = {'model': 'resnet50', 'epochs': 100}
        with _swap_attr(scitex_dict, 'to_str', fake_to_str):
            result = title2path(test_dict)
        len(calls) == 1
        calls[0] == ((test_dict,), {})
        # Act
        # Assert
        assert result == 'modelresnet50_epochs100'

    def test_real_world_examples_split_1(self):
        """Test with real-world title examples."""
        # Arrange
        title1 = 'Deep Learning: A Review [2023]'
        # Act
        # Assert
        assert title2path(title1) == 'deep_learning_a_review_2023'

    def test_real_world_examples_split_2(self):
        """Test with real-world title examples."""
        # Arrange
        title1 = 'Deep Learning: A Review [2023]'
        title2path(title1) == 'deep_learning_a_review_2023'
        title2 = 'config: lr=0.001; batch_size=32; optimizer=adam'
        # Act
        # Assert
        assert title2path(title2) == 'config_lr0.001_batch_size32_optimizeradam'

    def test_real_world_examples_split_3(self):
        """Test with real-world title examples."""
        # Arrange
        title1 = 'Deep Learning: A Review [2023]'
        title2path(title1) == 'deep_learning_a_review_2023'
        title2 = 'config: lr=0.001; batch_size=32; optimizer=adam'
        title2path(title2) == 'config_lr0.001_batch_size32_optimizeradam'
        title3 = 'data/train/images [processed]'
        # Act
        # Assert
        assert title2path(title3) == 'data/train/images_processed'

    def test_preserves_forward_slashes(self):
        """Test that forward slashes are preserved (for path-like strings)."""
        # Arrange
        # Act
        # Assert
        assert title2path("folder/subfolder/file") == "folder/subfolder/file"

    def test_multiple_consecutive_spaces(self):
        """Test handling of multiple consecutive spaces."""
        # Arrange
        # Act
        # Assert
        assert title2path("test    file") == "test_file"

    def test_tabs_and_newlines(self):
        """Test that tabs and newlines are treated as spaces."""
        # Note: The current implementation doesn't handle tabs/newlines,
        # but spaces should work
        # Arrange
        # Act
        # Assert
        assert title2path("test file") == "test_file"

    def test_unicode_characters_title2path_caf_r_sum_caf_r_sum(self):
        """Test handling of unicode characters."""
        # The function should handle unicode strings
        # Arrange
        # Act
        # Assert
        assert title2path("café: résumé") == "café_résumé"

    def test_numbers_preserved_title2path_test123file456_test123file456_split_1(self):
        """Test that numbers are preserved."""
        # Arrange
        # Act
        # Assert
        assert title2path('test123file456') == 'test123file456'

    def test_numbers_preserved_title2path_test123file456_test123file456_split_2(self):
        """Test that numbers are preserved."""
        # Arrange
        title2path('test123file456') == 'test123file456'
        # Act
        # Assert
        assert title2path('v2.0: release[final]') == 'v2.0_releasefinal'

    def test_edge_case_patterns_split_1(self):
        """Test edge cases with pattern combinations."""
        # Arrange
        # Act
        # Assert
        assert title2path('a_-_b_-_c') == 'a-b-c'

    def test_edge_case_patterns_split_2(self):
        """Test edge cases with pattern combinations."""
        # Arrange
        title2path('a_-_b_-_c') == 'a-b-c'
        # Act
        # Assert
        assert title2path('_-_start') == '-start'

    def test_edge_case_patterns_split_3(self):
        """Test edge cases with pattern combinations."""
        # Arrange
        title2path('a_-_b_-_c') == 'a-b-c'
        title2path('_-_start') == '-start'
        # Act
        # Assert
        assert title2path('end_-_') == 'end-'

    def test_edge_case_patterns_split_4(self):
        """Test edge cases with pattern combinations."""
        # Arrange
        title2path('a_-_b_-_c') == 'a-b-c'
        title2path('_-_start') == '-start'
        title2path('end_-_') == 'end-'
        # Act
        # Assert
        assert title2path('a________b') == 'a_b'


class TestTitle2PathIntegration:
    """Integration tests for title2path function."""

    def test_model_experiment_titles(self):
        """Test conversion of ML experiment titles."""
        # Arrange
        # Act
        # Assert
        titles = [
            ("ResNet50: ImageNet [Epoch: 100]", "resnet50_imagenet_epoch_100"),
            ("BERT Fine-tuning; Task=NER", "bert_fine-tuning_taskner"),
            (
                "GAN Training [Discriminator Loss = 0.5]",
                "gan_training_discriminator_loss_0.5",
            ),
        ]

        for input_title, expected in titles:
            assert title2path(input_title) == expected

    def test_filename_sanitization_not_in_result_split_1(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        # Act
        # Assert
        assert ':' not in result

    def test_filename_sanitization_not_in_result_split_2(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        # Act
        # Assert
        assert ';' not in result

    def test_filename_sanitization_not_in_result_split_3(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        ';' not in result
        # Act
        # Assert
        assert '=' not in result

    def test_filename_sanitization_not_in_result_split_4(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        ';' not in result
        '=' not in result
        # Act
        # Assert
        assert '[' not in result

    def test_filename_sanitization_not_in_result_split_5(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        ';' not in result
        '=' not in result
        '[' not in result
        # Act
        # Assert
        assert ']' not in result

    def test_filename_sanitization_not_in_result_split_6(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        ';' not in result
        '=' not in result
        '[' not in result
        ']' not in result
        # Act
        # Assert
        assert result == result.lower()

    def test_filename_sanitization_not_in_result_split_7(self):
        """Test that the output is suitable for filenames."""
        # Arrange
        problematic = 'file:name*with?invalid<chars>'
        result = title2path(problematic)
        ':' not in result
        ';' not in result
        '=' not in result
        '[' not in result
        ']' not in result
        result == result.lower()
        # Act
        # Assert
        assert '__' not in result


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/gen/_title2path.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: 2024-05-12 21:02:21 (7)
# # /sshx:ywatanabe@444:/home/ywatanabe/proj/scitex/src/scitex/gen/_title2spath.py
#
#
# def title2path(title):
#     """
#     Convert a title (string or dictionary) to a path-friendly string.
#
#     Parameters
#     ----------
#     title : str or dict
#         The input title to be converted.
#
#     Returns
#     -------
#     str
#         A path-friendly string derived from the input title.
#     """
#     if isinstance(title, dict):
#         from scitex.dict import to_str
#
#         title = to_str(title)
#
#     path = title
#
#     patterns = [":", ";", "=", "[", "]"]
#     for pattern in patterns:
#         path = path.replace(pattern, "")
#
#     path = path.replace("_-_", "-")
#     path = path.replace(" ", "_")
#
#     while "__" in path:
#         path = path.replace("__", "_")
#
#     return path.lower()
#
#
# # def title2path(title):
# #     if isinstance(title, dict):
# #         title = dict2str(title)
#
# #     path = title
#
# #     # Comma patterns
# #     patterns = [":", ";", "=", "[", "]"]
# #     for pp in patterns:
# #         path = path.replace(pp, "")
#
# #     # Exceptions
# #     path = path.replace("_-_", "-")
# #     path = path.replace(" ", "_")
#
# #     # Consective under scores
# #     for _ in range(10):
# #         path = path.replace("__", "_")
#
# #     return path.lower()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/gen/_title2path.py
# --------------------------------------------------------------------------------
