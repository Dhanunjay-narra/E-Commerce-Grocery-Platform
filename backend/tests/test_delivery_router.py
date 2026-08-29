from app.modules.delivery.router_optimizer import optimize_delivery_waypoints

def test_delivery_route_clustering():
    depot = (12.9716, 77.5946)
    pts = [(12.9750, 77.6000), (12.9900, 77.6200), (12.9720, 77.5950)]
    route = optimize_delivery_waypoints(depot, pts)
    assert len(route) == 3
    assert route[0] == (12.9720, 77.5950)
