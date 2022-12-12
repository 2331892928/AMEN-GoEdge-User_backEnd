from API import Api


class MetricStatService(Api):
    def listMetricStats(self):
        res = self.post(self.Host + "/MetricStatService/listMetricStats", json={
            "metricItemId": 1,
            "offset":0,
            "size":80
        })
        print(res.content.decode())
