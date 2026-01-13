class BusinessError(Exception):
    def __init__(self, message: str, code: str = "business_error"):
        super().__init__(message)
        self.message = message
        self.code = code

class NotFoundError(BusinessError):
    pass

class ValidationRuleError(BusinessError):
    pass
