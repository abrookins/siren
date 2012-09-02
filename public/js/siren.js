(function() {

    function getMap(coords) {
        var width = $('.container').width();
        var latlon=coords.latitude+","+coords.longitude;
        var imgUrl="http://maps.googleapis.com/maps/api/staticmap?center="
            +latlon+"&zoom=14&size="+width+"x200&sensor=false&markers=color:blue%7C"
            +latlon+'&scale=2';
        console.log(imgUrl);

        $('#map').html("<img src='"+imgUrl+"' />");
    }

    function getCrimes(loc) {
        $.get('/api/crime_stats?point=' + loc.coords.latitude + ',' + loc.coords.longitude, function(data) {

            $.each(data.result.stats, function () {
                var crime = this[0];
                var numCrimes = this[1];
                var colorClass = "success";

                if (numCrimes > 25 && numCrimes <= 100) {
                    colorClass = 'info';
                } else if (numCrimes > 100) {
                    colorClass = 'error';
                }

                var tr = $('<tr/>').appendTo($('#crimes')).addClass(colorClass);

                $('<td/>').text(numCrimes).appendTo(tr);
                $('<td/>').text(crime).appendTo(tr);
                $('<td/>').appendTo(tr);
            });

            getMap(loc.coords);
        });
    }

    function reportError(err) {
        console.log(err);
        alert('Could not get your location. Try enabling location services.')
    }

    $(document).ready(function () {
        navigator.geolocation.getCurrentPosition(getCrimes, reportError);
    });
})();
