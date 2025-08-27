from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder


encoder = HuggingFaceEncoder(name = "sentence-transformers/all-MiniLM-L6-v2")

faq_data = Route(
    name = "faq",
    utterances=[
    "What is the return policy of the products?",
    "Do I get discount with the HDFC credit card?",
    "How can I track my order?",
    "What payment methods are accepted?",
    "How long does it take to process a refund?",
    "Are there any ongoing sales or promotions?",
    "Do you offer international shipping?"
    ],
    score_threshold = 0.2
)

sql = Route(
    name = "sql",
    utterances = [
        "I want to buy nike shoes that have 50% discount",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of Puma running shoes?"
    ],
    score_threshold = 0.25
    )
small_talk = Route(
    name = "small_talk",
    utterances = [
        "Hello",
        "Hi there",
        "How are you?",
        "Good morning",
        "What's up?",
        "Thanks for your help",
        "Thank you",
        "You're awesome",
        "Can you help me?",
        "I need assistance",
        "Who are you?"
    ],
    score_threshold = 0.25
)




routes = [faq_data, sql, small_talk]
router = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")




