"""now() must follow the dataset clock, not the wall clock."""
import datetime as dt
from copilot import agent
from copilot import tools as T


def test_now_follows_dataset_today_when_sim_day_unset():
    """The sample dataset's 'today' is AIC_TODAY (default 2026-10-17).

    earlier_wells and stored facts compare dates against now()[:10]. If SIM_DAY
    is unset, the default server path used wall-clock datetime.now(), so on
    2026-11-10 a conversation was stamped 24 days in the future of the dataset
    and 'yesterday' lookups compared against the wrong cutoff.
    """
    prev = agent.SIM_DAY
    try:
        agent.SIM_DAY = None
        assert agent.now()[:10] == str(T.TODAY)
        agent.SIM_DAY = 0
        assert agent.now()[:10] == str(T.TODAY)
        agent.SIM_DAY = 2
        assert agent.now()[:10] == str(T.TODAY + dt.timedelta(days=2))
    finally:
        agent.SIM_DAY = prev
