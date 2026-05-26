import pytest

from collectoss.tasks.github.util.util import sanity_check_email, extract_email

class TestSanityCheckEmail:

    @pytest.mark.unit
    def test_simple_valid_emails(self):
        assert sanity_check_email("user@example.com") == "user@example.com"

        #This is the primary real-world use case per the caller in facade_github.
        result = sanity_check_email("12345+username@users.noreply.github.com")
        assert result == "12345+username@users.noreply.github.com"

    @pytest.mark.unit
    def test_simple_valid_emails_with_padding(self):
        assert sanity_check_email(" user@example.com ") == "user@example.com"

        #This is the primary real-world use case per the caller in facade_github.
        result = sanity_check_email(" 12345+username@users.noreply.github.com ")
        assert result == "12345+username@users.noreply.github.com"


    @pytest.mark.unit
    def test_email_with_plus_addressing(self):
        assert sanity_check_email("user+tag@example.com") == "user+tag@example.com"

    @pytest.mark.unit
    def test_email_with_dots_in_local(self):
        assert sanity_check_email("first.last@example.com") == "first.last@example.com"

    @pytest.mark.unit
    def test_email_with_subdomain(self):
        assert sanity_check_email("user@mail.example.co.uk") == "user@mail.example.co.uk"

    @pytest.mark.unit
    def test_non_ascii(self):
        assert sanity_check_email("üser@example.com") is None
        assert sanity_check_email("user@exämple.com") is None
        assert sanity_check_email("user😀@example.com") is None

class TestSanityCheckEmailEdgeCasesInput:

    @pytest.mark.unit
    def test_integer_input_returns_none(self):
        with pytest.raises(TypeError):
            assert sanity_check_email(42) is None

    @pytest.mark.unit
    def test_boolean_input_returns_none(self):
        with pytest.raises(TypeError):
            assert sanity_check_email(True) is None


class TestSanityCheckEmailEdgeCases:

    @pytest.mark.unit
    def test_at_sign_only(self):
        assert sanity_check_email("@") is None

    @pytest.mark.unit
    def test_at_sign_with_domain_no_local(self):
        assert sanity_check_email("@example.com") is None

    @pytest.mark.unit
    def test_local_with_at_no_domain(self):
        assert sanity_check_email("user@") is None

    @pytest.mark.unit
    def test_multiple_at_signs(self):
        assert sanity_check_email("user@@example.com") is None


class TestEmailExtraction:

    @pytest.mark.unit
    def test_embedded_email_in_text_returns_email(self):
        """This is intended to test cases where the user put their name and email in the same field, either before or after"""
        assert extract_email("Name user@example.com and more") == 'user@example.com'