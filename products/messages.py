class MessageTemplates:
    messages = {
        "CREATED_SUCCESSFULLY": "{entity_name} '{entity_id}' has been created successfully.",
        "UPDATE_SUCCESS": "{entity_name} with ID {entity_id} updated successfully.",
        "API_PAYLOAD_ERRROR": "Wrong API Formatting, Expected payload tye List/Array. Passed {payload_type}",
        "REQUIRED_FIELDS_MISSING": "Missing mandatory fields {missing_fields}",
        "NOT_FOUND": "No {entity_name} found matching the criteria",
        "ID_EXISTS": "{entity_name} ID already exists: {entity_id}",
        "ID_NOT_EXISTS": "{entity_name} ID does not exists: {entity_id}",
        "NO_CHANGE": "{entity_name} ID {entity_id}: No Changes compared to existing values",
        "IMAGE_SAVE_FAILED": "Failed to save image for {entity_name} ID: {entity_id}",
        "DATABASE_ERROR": "Database error Occured: {error}",
        "UNEXPECTED_ERROR": "Unexpected error Occured: {error}",
        "AUDIT_LOGGING_ERROR": "Error in audit logging for {entity_name}",
        "ACCESS_DENIED": "Access denied for user {username}.",
        "GENERIC_ERROR": "An error occurred: {error_message}",
        "WELCOME_MESSAGE": "Welcome {username}, have a great day!",
        "PAGINATION_INFO": "Displaying page {page_number} with {page_size} results per page."
    }

    @staticmethod
    def get_message(key, **kwargs):
        """
        Retrieves and formats a message template by key.

        :param key: The message key.
        :param kwargs: Variables to replace in the template.
        :return: A formatted message string.
        """
        template = MessageTemplates.messages.get(key, "Message template not found.")
        return template.format(**kwargs)
