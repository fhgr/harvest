starting_words = \
     ("Hello", "Hi", "Hey", "Have", "Quote from", "I ", "I'", "Is ", "You", "Why", "Where ", "Thank", "Welcome",
      "The ", "A ", "Here", "Can ", "Could ", "Some ", "For ", "Ok", "Since", "If ", "May ", "Do ", "This ", "When",
      "That", "My", "Yes", "No", "Are", "How", "There", "Also", "We ", "Mostly", "Due", "What", "Does", "Lovely",
      "Would", "Please", "Oh ", "Still", "Other ", "Full Name:", "Today", "Just",
      "Hallo", "Hi", "Moin", "So", "Ich", "Wie ", "Was ", "F\u00fcr", "Da ", "Danke", "Willkommen", "Zitat", "Es ",
      "Eine ", "Du ", "Sch\u00f6nen", "Vielen ", "Mir", "Habe", "Bei", "Guten", "Der", "Liebe", "Super", "Frage",
      "Nur", "Das", "Gibt", "Hast", "War", "Sollte", "Wenn", "Dazu", "In ", "Wirklich", "Man ", "Auf", "Ja", "Nein",
      "Hier", "Jetzt", "Leider", "Hoffe", "Solange", "Von", "Zu ", "Damit",
      "Bonjour", "Bonsoir", "Je", "les ", "Oui", "C'est ", "Merci", "Bienvenue", "Pour ", "La ", "Le ",
      "Hola", "Perdon", "Me ", "Quer\u00eda ", "Juanjo", "Buenas ")


def split_into_posts(text):
    passages = [passage.lstrip() for passage in text.split('\n')]
    posts = []
    post = ""
    for passage in passages:
        if passage.startswith(starting_words) and post:
            posts.append(post)
            post = passage
        else:
            post = post + passage
    if post:
        posts.append(post)
    return posts
