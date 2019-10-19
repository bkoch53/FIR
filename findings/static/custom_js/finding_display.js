$(function () {
	function refresh_finding_display(container) {
		return function(data) {
			container.html(data);

			container.find('.relative-date').each(function() {
      			then = moment($(this).text(), 'YYYY-MM-DD HH:mm').fromNow();
      			$(this).text(then);
    		});
		};
	}

	function refresh_display(element) {
		var finding_table = element.closest('.finding_table');
		var container;
		if (element.hasClass('finding_display')) {
			container = element;
		}
		else {
			container = element.closest('.finding_display');
		}

		var order_by = finding_table.data('order-param') || 'date';
		var asc = finding_table.data('asc') || false;

		var field = element.data('sort');
		if (field) {
			if (field == order_by) {
				asc = !asc;
			}
			else {
				order_by = field;
			}
		}

		var url = container.data('url');
		var q = container.data('query');

		page = element.data('page') || 1;

		$.get(url, { 'order_by': order_by, 'asc': asc, 'q': q, 'page': page }, refresh_finding_display(container));
	}

	function toggle_star(link) {
		return function(data) {
			var i = link.find('i.star');
    		i.toggleClass('glyphicon-star');
    		i.toggleClass('glyphicon-star-empty');

    		var starred_findings = $('#starred_findings');
			if (starred_findings.length > 0) {
				refresh_display(starred_findings);
			}
		}
	}

	// Make sure each 'finding_display' comes to life
	$('.finding_display').each(function (index) {
		refresh_display($(this));
	});

	// Change sort when clicking on a column title
	$('.finding_display').on('click', 'thead a', function (observation) {
		refresh_display($(this));

		observation.probservationDefault();
	});

	// Change page when clicking on a pagination link
	$('.finding_display').on('click', 'a.paginate', function(observation) {
		refresh_display($(this));

		observation.probservationDefault();
	});

	// Star/Unstar findings
	$('.finding_display').on('click', 'a.star', function(observation) {
		var link = $(this);
		var url = link.attr('href');
		$.getJSON(url, toggle_star(link));

		observation.probservationDefault();
	});

});
