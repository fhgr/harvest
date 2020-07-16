"""
Starting words:
en = ("Hello", "Hi", "Hey", "Have", "Quote from", "I ", "I'", "Is ", "You", "Why", "Where ", "Thank", "Welcome",
      "The ", "A ", "Here", "Can ", "Could ", "Some ", "For ", "Ok", "Since", "If ", "May ", "Do ", "This ", "When",
      "That", "My", "Yes", "No", "Are", "How", "There", "Also", "We ", "Mostly", "Due", "What", "Does", "Lovely",
      "Would", "Please", "Oh ", "Still", "Other ", "Full Name:", "Today", "Just")
de = ("Hallo", "Hi", "Moin", "So", "Ich", "Wie ", "Was ", "F\u00fcr", "Da ", "Danke", "Willkommen", "Zitat", "Es ",
      "Eine ", "Du ", "Sch\u00f6nen", "Vielen ", "Mir", "Habe", "Bei", "Guten", "Der", "Liebe", "Super", "Frage", 
      "Nur", "Das", "Gibt", "Hast", "War", "Sollte", "Wenn", "Dazu", "In ", "Wirklich", "Man ", "Auf", "Ja", "Nein",
      "Hier", "Jetzt", "Leider", "Hoffe", "Solange", "Von", "Zu ", "Damit")
fr = ("Bonjour", "Bonsoir", "Je", "les ", "Oui", "C'est ", "Merci", "Bienvenue", "Pour ", "La ", "Le ")
sp = ("Hola", "Perdon", "Me ", "Quer\u00eda ", "Juanjo", "Buenas ")
"""

from dragnet import extract_content_and_comments
from harvest.date_search import search_dates


def date_in_header(text):
    return search_dates(text) and len(text) < 120


def get_posts(html):
    content_comments = extract_content_and_comments(html, encoding=None, as_blocks=True)

    return [c.text.decode("utf-8") for c in content_comments
            if not date_in_header(c.text.decode("utf-8"))]
