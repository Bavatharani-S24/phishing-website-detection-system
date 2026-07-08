import re
from urllib.parse import urlparse

def extract_features(url):

    parsed = urlparse(url)
    domain = parsed.netloc

    features = []

    # 1 Having @ symbol
    features.append(1 if "@" in url else 0)

    # 2 Having IP
    features.append(1 if re.match(r"\d+\.\d+\.\d+\.\d+", domain) else 0)

    # 3 Path length
    features.append(1 if len(parsed.path) > 10 else 0)

    # 4 Prefix suffix (-)
    features.append(1 if "-" in domain else 0)

    # 5 Protocol (http = suspicious)
    features.append(1 if parsed.scheme == "http" else 0)

    # 6 Redirection //
    features.append(1 if url.rfind("//") > 7 else 0)

    # 7 Sub domains
    features.append(domain.count("."))

    # 8 URL Length
    features.append(1 if len(url) > 75 else 0)

    # 9 Age domain (approx)
    features.append(0)

    # 10 DNS record (approx)
    features.append(0)

    # 11 Domain registration length (approx)
    features.append(0)

    # 12 HTTP tokens
    features.append(1 if "http" in domain else 0)

    # 13 Statistical report (approx)
    suspicious_words = ["login","verify","update","secure","account","bank","paypal"]
    features.append(1 if any(word in url.lower() for word in suspicious_words) else 0)

    # 14 Tiny URL
    shorteners = ["bit.ly","tinyurl","goo.gl","t.co","ow.ly"]
    features.append(1 if any(short in url for short in shorteners) else 0)

    # 15 Web traffic (approx)
    features.append(0)

    return features



