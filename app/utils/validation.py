def validate_50_words(text: str):
    words = text.split()
    return 10 <= len(words) <= 55



def validate_media(media_type: str, media_url: str):
    if media_type not in ["image", "video"]:
        return False
    if not media_url or media_url.strip() == "":
        return False
    return True
