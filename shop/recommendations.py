"""Product recommendations (no extra database tables needed).

What the shopper has shown interest in is collected from:
    * pieces they viewed recently      (kept in the session)
    * their wishlist
    * their cart
    * their past orders
Each of those pieces "votes" for its category, material and gender and for a price range.
Every other available piece is then scored by how well it matches those votes:

    same category   +3.0      same material +2.0      same gender +1.0
    price close to what they look at  up to +1.5
    featured +0.3 / new arrival +0.2      (tiny tie-breakers, newest first)

If there is nothing to learn from yet (new visitor) or the list is short, it is filled
with featured pieces, then new arrivals, then the newest pieces - so a section is never empty
while the shop has products.

    recommend_for(request, limit=8)                 -> "Recommended for you" (home, cart)
    similar_to(request, product, limit=4)           -> "You may also like"   (product page)
    record_view(request, product_id)                -> call when a product page is opened
"""
from collections import Counter

from .models import Cart, Order, Product, Wishlist

SESSION_KEY = "recently_viewed"
MAX_VIEWED = 12


# --------------------------------------------------------------------------- recently viewed
def record_view(request, product_id):
    viewed = [pid for pid in request.session.get(SESSION_KEY, []) if pid != product_id]
    request.session[SESSION_KEY] = ([product_id] + viewed)[:MAX_VIEWED]


def recently_viewed_ids(request):
    return [int(pid) for pid in request.session.get(SESSION_KEY, []) if str(pid).isdigit()]


# --------------------------------------------------------------------------- shopper signals
def _signals(request):
    """-> (weights {product_id: weight}, ids to keep out of the list). Never raises."""
    weights, owned = Counter(), set()
    try:
        for rank, pid in enumerate(recently_viewed_ids(request)):
            weights[pid] += 2.0 / (1 + rank * 0.5)          # most recent view counts most
        user = request.user
        if user.is_authenticated:
            for pid in Wishlist.objects.filter(user=user).values_list("product_id", flat=True):
                weights[pid] += 2.5
            cart = Cart.objects.filter(user=user).first()
            if cart:
                for pid in cart.items.values_list("product_id", flat=True):
                    weights[pid] += 3.0
                    owned.add(pid)                           # already in the cart: do not suggest again
            for order in Order.objects.filter(user=user).exclude(status="cancelled").prefetch_related("items").order_by("-pk")[:20]:
                for item in order.items.all():
                    if item.product_id:
                        weights[item.product_id] += 1.5
                        owned.add(item.product_id)
    except Exception as exc:                                 # recommendations must never break a page
        print("Recommendation signals failed:", exc)
    return weights, owned


def _profile(weights, extra=None):
    """Turn the weighted products into category / material / gender votes and an average price."""
    ids = set(weights) | set(extra or {})
    cats, mats, gens, price_sum, price_w = Counter(), Counter(), Counter(), 0.0, 0.0
    merged = Counter(weights)
    for pid, w in (extra or {}).items():
        merged[pid] += w
    for p in Product.objects.filter(pk__in=ids):
        w = merged[p.pk]
        cats[p.category_id] += w
        mats[p.material] += w
        gens[p.gender] += w
        if p.price is not None:
            price_sum += float(p.price) * w
            price_w += w
    return cats, mats, gens, (price_sum / price_w if price_w else None)


def _score(p, cats, mats, gens, avg_price, seen):
    def share(counter, key):                                 # 0..1: how much of the interest points at this value
        total = sum(counter.values())
        return counter[key] / total if total else 0.0

    s = 3.0 * share(cats, p.category_id) + 2.0 * share(mats, p.material) + 1.0 * share(gens, p.gender)
    if avg_price and p.price is not None:
        gap = abs(float(p.price) - avg_price) / avg_price    # 0 = same price, 1+ = very different
        s += 1.5 * max(0.0, 1.0 - gap)
    if getattr(p, "is_featured", False):
        s += 0.3
    if getattr(p, "is_new_arrival", False):
        s += 0.2
    if p.pk in seen:
        s -= 0.5                                             # already looked at: show new things first
    return s


def _available():
    return Product.objects.filter(is_available=True, stock__gt=0).select_related("category")


def _fill(picked, limit, banned):
    """Top the list up with featured, then new, then newest pieces."""
    have = {p.pk for p in picked} | set(banned)
    for qs in (_available().filter(is_featured=True).order_by("-created_at"),
               _available().filter(is_new_arrival=True).order_by("-created_at"),
               _available().order_by("-created_at")):
        for p in qs:
            if len(picked) >= limit:
                return picked
            if p.pk not in have:
                picked.append(p)
                have.add(p.pk)
    return picked


# --------------------------------------------------------------------------- public API
def recommend_for(request, limit=8, exclude=()):
    """Pieces picked for this shopper (home page, cart)."""
    weights, owned = _signals(request)
    banned = set(owned) | set(exclude)
    picked = []
    if weights:
        cats, mats, gens, avg = _profile(weights)
        seen = set(recently_viewed_ids(request))
        pool = [p for p in _available() if p.pk not in banned]
        pool.sort(key=lambda p: (-_score(p, cats, mats, gens, avg, seen), -p.created_at.timestamp()))
        picked = [p for p in pool if _score(p, cats, mats, gens, avg, seen) > 0.3][:limit]
    return _fill(picked, limit, banned)


def similar_to(request, product, limit=4):
    """Pieces like `product` (same category / material / gender / price), nudged by the shopper's own taste."""
    weights, owned = _signals(request)
    banned = {product.pk}
    cats, mats, gens, avg = _profile(weights, extra={product.pk: 6.0})   # the product being viewed leads
    seen = set(recently_viewed_ids(request))
    pool = [p for p in _available() if p.pk not in banned]
    pool.sort(key=lambda p: (-_score(p, cats, mats, gens, avg, seen), -p.created_at.timestamp()))
    picked = pool[:limit]
    return _fill(picked, limit, banned)


def wishlist_ids(request):
    if not request.user.is_authenticated:
        return set()
    return set(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))
