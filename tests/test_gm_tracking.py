from bot import GMTracker


def test_missing_gm_users_uses_static_roster():
    tracker = GMTracker(static_user_ids={1, 2, 3})
    tracker.record_gm(user_id=1, username=None)
    tracker.record_gm(user_id=2, username=None)

    assert tracker.get_missing_participants() == ["id:3"]


def test_missing_gm_users_uses_active_participants_and_username_keys():
    tracker = GMTracker(static_user_ids=None)
    tracker.record_activity(user_id=10, username="alice")
    tracker.record_activity(user_id=20, username="bob")
    tracker.record_gm(user_id=10, username="alice")

    assert tracker.get_missing_participants() == ["bob"]

