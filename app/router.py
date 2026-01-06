from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(name = 'sentence-transformers/all-distilroberta-v1',score_threshold=0.35)

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        'Are there any ongoing sales or promotions?',
        'Can I cancel or modify my order after placing it?',
        'Do you offer international shipping?',
        'What should I do if I receive a damaged product?',
        'How do I use a promo code during checkout?'
    ]
)

product_search = Route(
    name = 'product_search',
    utterances = [
        'I want to buy nike shoes that have 50% discount.',
        'Are there any shoes under Rs. 3000?',
        'Do you have formal shoes in size 9?',
        'Are there any Puma shoes on sale?',
        'What is the price of puma running shoes?'
    ]
)
small_talk = Route(
    name = 'small_talk',
    utterances = ['How are you?',
                  "What's your name?",
                  "Are you a robot?",
                  "What do you do?",
                  "What are you?",
                  "What's the timing right now",
                  "Hello",
                  "Hello, how are you?",
                  "What's the time right now?"
                  ]
)
router = SemanticRouter(routes = [faq, product_search,small_talk],encoder = encoder,auto_sync="local")

if __name__ == '__main__':
    print(router("What's the return policy?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)
    print(router('How can I track my order?').name)
