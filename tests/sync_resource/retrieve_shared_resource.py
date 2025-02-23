from unittest.mock import Mock

from vedro import params
from vedro_fn import given, scenario, then, when

from vedro_shared_resource import shared_resource


def add(a, b):
    return a + b


@scenario
def retrieve_resource_on_first_access():
    with given:
        mock = Mock(side_effect=add)
        memoized = shared_resource()(mock)

    with when:
        result = memoized(1, 2)

    with then:
        assert result == 3
        assert mock.call_count == 1


@scenario
def retrieve_cached_resource_on_subsequent_access():
    with given:
        mock = Mock(side_effect=add)
        memoized = shared_resource()(mock)
        memoized(1, 2)

    with when:
        result = memoized(1, 2)

    with then:
        assert result == 3
        assert mock.call_count == 1


@scenario
def retrieve_resource_after_eviction():
    with given:
        mock = Mock(side_effect=add)
        memoized = shared_resource(max_instances=1)(mock)
        memoized(1, 2)  # 1st instance
        memoized(2, 1)  # 2nd instance, so 1st instance should be removed

        mock.reset_mock()

    with when:
        result = memoized(1, 2)

    with then:
        assert result == 3
        assert mock.call_count == 1


@scenario
def retrieve_distinct_resources_for_different_arguments():
    with given:
        mock = Mock(side_effect=add)
        memoized = shared_resource()(mock)
        memoized(1, 2)

    with when:
        result = memoized(2, 1)

    with then:
        assert result == 3
        assert mock.call_count == 2


@scenario([
    params(type_sensitive=True, mock_call_count=2),
    params(type_sensitive=False, mock_call_count=1),
])
def retrieve_resource_respecting_type_sensitivity(type_sensitive: bool, mock_call_count: int):
    with given:
        mock = Mock(side_effect=add)
        memoized = shared_resource(type_sensitive=type_sensitive)(mock)
        memoized(1, 2)

    with when:
        result = memoized(1.0, 2.0)

    with then:
        assert result == 3.0
        assert mock.call_count == mock_call_count
