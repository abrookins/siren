(function () {
    window.org == undefined ? window.org = {} : window.org;
    window.org.pdxcrime == undefined ? window.org.pdxcrime = {} : window.org.pdxcrime;

    function SirenApi(opts) {
        this.baseUrl = opts.baseUrl;
        _.bindAll(this);
    }

    SirenApi.prototype = {
        initialize: function() {
            navigator.geolocation.getCurrentPosition(
                this.getCrimeStats, this.reportError);
        },

        getMap: function (coords) {
            var width = $('.container').width();
            var latlon = coords.latitude + "," + coords.longitude;
            var imgUrl = "http://maps.googleapis.com/maps/api/staticmap?center="
                + latlon + "&zoom=14&size=" + width + "x200&sensor=false&markers=color:blue%7C"
                + latlon + '&scale=2&key=AIzaSyDSAgYb3WH9ukHVggvQKaBJUKNyGzh6MqQ';

            $('#map').html("<img src='" + imgUrl + "' />");
        },

        makeTable: function (tableEl, data) {
            $.each(data.result.stats, function () {
                var crime = this[0];
                var numCrimes = this[1];
                var colorClass = "success";

                if (numCrimes > 25 && numCrimes <= 100) {
                    colorClass = 'info';
                } else if (numCrimes > 100) {
                    colorClass = 'error';
                }

                var tr = $('<tr/>').appendTo($(tableEl)).addClass(colorClass);

                $('<td/>').text(crime).appendTo(tr);
                $('<td/>').text(numCrimes).appendTo(tr);
            });
        },

        makeApiRequest: function (opts) {
            var coords = opts.loc.coords;
            var _this = this;

            $('#longitude').text(coords.longitude);
            $('#latitude').text(coords.latitude);

            $.ajax({
                url: opts.url,
                type: "GET",
                dataType: "jsonp",
                success: function (data) {
                    _this.makeTable(opts.tableEl, data);
                    _this.getMap(opts.loc.coords);
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown);
                    alert("Could not contact server! Try again later.");
                }
            });
        },

        getCrimeStats: function (loc) {
            var now = new Date();
            this.makeApiRequest({
                loc: loc,
                url: this.baseUrl + '/crimes/near/' + loc.coords.latitude + ',' + loc.coords.longitude + '/stats',
                tableEl: '#all-crimes-table'
            });
            this.makeApiRequest({
                loc: loc,
                url: this.baseUrl + '/crimes/near/' + loc.coords.latitude + ',' + loc.coords.longitude + '/filter/hour/' + now.getHours() + '/stats',
                tableEl: '#crimes-hour-table'
            });
        },

        reportError: function (err) {
            console.log(err);
            alert('Could not get your location. Try enabling location services.')
        }
    };

    window.org.pdxcrime.SirenApi = SirenApi;
})();
