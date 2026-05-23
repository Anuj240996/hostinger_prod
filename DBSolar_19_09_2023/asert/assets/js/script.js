/*
Author       : Dreamguys
Template Name: Preskool - Bootstrap Admin Template
Version      : 1.0
*/

(function($) {
    "use strict";
	
	// Variables declarations
	
	var $wrapper = $('.main-wrapper');
	var $pageWrapper = $('.page-wrapper');
	var $slimScrolls = $('.slimscroll');
	
	// Sidebar
	
	var Sidemenu = function() {
		this.$menuItem = $('#sidebar-menu a');
	};

	/**
	 * Templates use {% active_link %} on <li class="submenu"> for firereport (complaint) URLs.
	 * CSS keeps .sidebar-menu ul ul { display: none }. The old line only looked for a.active
	 * and .trigger('click'), so complaint pages never opened the Consumer Complaint branch.
	 */
	function expandSidebarActiveBranches() {
		var $root = $('#sidebar-menu');
		if (!$root.length) {
			return;
		}
		$root.find('li.submenu').each(function() {
			var $li = $(this);
			var hasActiveLi = $li.hasClass('active');
			var hasActiveLink = $li.find('a.active').length > 0;
			if (!hasActiveLi && !hasActiveLink) {
				return;
			}
			var $toggle = $li.children('a').first();
			var $sub = $toggle.next('ul');
			if (!$sub.length) {
				return;
			}
			$toggle.addClass('subdrop');
			$sub.css('display', 'block');
		});
	}
	
	function init() {
		var $this = Sidemenu;
		// Only treat <a> as a submenu toggle when it is immediately followed by <ul>.
		// BUGFIX: Old code used $('ul', $a.parents('ul:first')).slideUp() which targets EVERY
		// nested ul under the root sidebar list — including the submenu we are opening — so the
		// menu flashed open then immediately slid shut. Only close *sibling* branches at the same level.
		$('#sidebar-menu a').off('click.sidemenu').on('click.sidemenu', function(e) {
			var $a = $(this);
			var $nextUl = $a.next('ul');
			if (!$nextUl.length) {
				return;
			}
			e.preventDefault();
			e.stopPropagation();

			var $ownLi = $a.parent('li');
			var $parentUl = $ownLi.parent('ul');

			if (!$a.hasClass('subdrop')) {
				$parentUl.children('li').each(function() {
					var $peerLi = $(this);
					if ($peerLi[0] === $ownLi[0]) {
						return;
					}
					var $peerA = $peerLi.children('a').first();
					var $peerSub = $peerA.next('ul');
					if ($peerSub.length) {
						$peerSub.stop(true, true).slideUp(200);
						$peerA.removeClass('subdrop');
					}
				});
				$nextUl.stop(true, true).slideDown(200);
				$a.addClass('subdrop');
			} else {
				$a.removeClass('subdrop');
				$nextUl.stop(true, true).slideUp(200);
			}
		});
		expandSidebarActiveBranches();
	}
	
	// Sidebar Initiate
	init();
	$(window).on('load', expandSidebarActiveBranches);
	
	// Mobile menu sidebar overlay
	
	$('body').append('<div class="sidebar-overlay"></div>');
	$(document).on('click', '#mobile_btn', function() {
		$wrapper.toggleClass('slide-nav');
		$('.sidebar-overlay').toggleClass('opened');
		$('html').addClass('menu-opened');
		return false;
	});
	
	// Sidebar overlay
	
	$(".sidebar-overlay").on("click", function () {
		$wrapper.removeClass('slide-nav');
		$(".sidebar-overlay").removeClass("opened");
		$('html').removeClass('menu-opened');
	});
	
	// Page Content Height
	
	if($('.page-wrapper').length > 0 ){
		var height = $(window).height();	
		$(".page-wrapper").css("min-height", height);
	}
	
	// Page Content Height Resize
	
	$(window).resize(function(){
		if($('.page-wrapper').length > 0 ){
			var height = $(window).height();
			$(".page-wrapper").css("min-height", height);
		}
	});
	
	// Select 2
	
    if ($('.select').length > 0) {
        $('.select').select2({
            minimumResultsForSearch: -1,
            width: '100%'
        });
    }
	
	// Datetimepicker
	
	if($('.datetimepicker').length > 0 ){
		$('.datetimepicker').datetimepicker({
			format: 'DD-MM-YYYY',
			icons: {
				up: "fas fa-angle-up",
				down: "fas fa-angle-down",
				next: 'fas fa-angle-right',
				previous: 'fas fa-angle-left'
			}
		});
		$('.datetimepicker').on('dp.show',function() {
			$(this).closest('.table-responsive').removeClass('table-responsive').addClass('temp');
		}).on('dp.hide',function() {
			$(this).closest('.temp').addClass('table-responsive').removeClass('temp')
		});
	}

	// Tooltip
	
	if($('[data-toggle="tooltip"]').length > 0 ){
		$('[data-toggle="tooltip"]').tooltip();
	}
	
	// Datatable (global tools for every table.datatable)
	function stripHtmlForExport(html) {
		try {
			var doc = new DOMParser().parseFromString(String(html || ''), 'text/html');
			return doc.body.textContent || "";
		} catch (e) {
			return String(html || '');
		}
	}

	function getExportDataForTable(table) {
		var visibleCols = table.columns(':visible').indexes().toArray().filter(function(colIndex) {
			var header = (table.column(colIndex).header().innerText || '').trim();
			return header !== 'Action';
		});
		var headers = visibleCols.map(function(colIndex) {
			return (table.column(colIndex).header().innerText || '').trim();
		});
		var rowIndexes = table.rows({ search: 'applied', order: 'applied' }).indexes().toArray();
		var body = rowIndexes.map(function(rowIdx, displayIdx) {
			return visibleCols.map(function(colIndex) {
				var header = (table.column(colIndex).header().innerText || '').trim();
				if (header === 'Sr No.') return displayIdx + 1;
				var cellHtml = table.cell(rowIdx, colIndex).render('display');
				return String(stripHtmlForExport(cellHtml) || '').replace(/\s+/g, ' ').trim();
			});
		});
		return [headers].concat(body);
	}

	function getCompanyHeaderLines() {
		return [
			'DB SOLAR',
			'DB Solar - Paithan, Maharashtra, India'
		];
	}

	var _dtColumnOrderModalBound = false;

	function ensureDtColumnOrderModal() {
		if ($('#dtColumnOrderModal').length) return;
		$('body').append(
			'<div class="modal fade" id="dtColumnOrderModal" tabindex="-1" role="dialog" aria-labelledby="dtColumnOrderModalLabel" aria-hidden="true">' +
			'  <div class="modal-dialog modal-dialog-scrollable" role="document">' +
			'    <div class="modal-content">' +
			'      <div class="modal-header py-2">' +
			'        <h5 class="modal-title" id="dtColumnOrderModalLabel">Columns</h5>' +
			'        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
			'      </div>' +
			'      <div class="modal-body">' +
			'        <p class="small text-muted mb-2">Check columns in the order they should appear (left to right, between Sr No. and Action). Uncheck to hide.</p>' +
			'        <div class="dt-col-modal-checkboxes border rounded p-2 mb-3" style="max-height:240px;overflow-y:auto;"></div>' +
			'        <div class="mb-1"><strong>Selection order</strong></div>' +
			'        <ol class="dt-col-modal-order-list small mb-0 pl-3"></ol>' +
			'      </div>' +
			'      <div class="modal-footer py-2">' +
			'        <button type="button" class="btn btn-sm btn-secondary" data-dismiss="modal">Cancel</button>' +
			'        <button type="button" class="btn btn-sm btn-primary dt-col-modal-generate-btn">Generate Table</button>' +
			'      </div>' +
			'    </div>' +
			'  </div>' +
			'</div>'
		);
	}

	function dtOrigFromCurrent(table, curIdx) {
		if (table.colReorder && typeof table.colReorder.transpose === 'function') {
			return table.colReorder.transpose(curIdx, 'fromCurrent');
		}
		return curIdx;
	}

	function dtCurrentFromOrig(table, origIdx) {
		if (table.colReorder && typeof table.colReorder.transpose === 'function') {
			return table.colReorder.transpose(origIdx, 'toCurrent');
		}
		return origIdx;
	}

	function getDtColumnLayout(table) {
		var n = table.columns().count();
		var cols = [];
		var srNoOrig = null;
		var actionOrig = null;
		var i;
		for (i = 0; i < n; i++) {
			var orig = dtOrigFromCurrent(table, i);
			var th = table.column(i).header();
			var name = (th.innerText || th.textContent || '').trim();
			var isSr = name === 'Sr No.';
			var isAction = name === 'Action';
			var selectable = !!(name && !isSr && !isAction);
			if (isSr) srNoOrig = orig;
			if (isAction) actionOrig = orig;
			cols.push({ current: i, orig: orig, name: name, selectable: selectable });
		}
		return { cols: cols, srNoOrig: srNoOrig, actionOrig: actionOrig, count: n };
	}

	function getDtDisplayOrderOriginals(table) {
		if (table.colReorder && typeof table.colReorder.order === 'function') {
			return table.colReorder.order();
		}
		var n = table.columns().count();
		var a = [];
		for (var i = 0; i < n; i++) a.push(i);
		return a;
	}

	function updateDtColumnModalOrderList($modal) {
		var order = $modal.data('selectionOrder') || [];
		var nameByOrig = $modal.data('nameByOrig') || {};
		var $ol = $modal.find('.dt-col-modal-order-list');
		$ol.empty();
		order.forEach(function(orig) {
			var label = nameByOrig[orig] != null ? nameByOrig[orig] : ('Column ' + orig);
			$ol.append($('<li></li>').text(label));
		});
	}

	function syncDtColumnSelectAllState($modal) {
		var $cbs = $modal.find('.dt-col-cb');
		var n = $cbs.length;
		var checked = $cbs.filter(':checked').length;
		$modal.find('.dt-col-select-all').prop('checked', n > 0 && checked === n);
	}

	function populateDtColumnOrderModal(table) {
		ensureDtColumnOrderModal();
		var $modal = $('#dtColumnOrderModal');
		var layout = getDtColumnLayout(table);
		var displayOrder = getDtDisplayOrderOriginals(table);
		var nameByOrig = {};
		layout.cols.forEach(function(c) {
			nameByOrig[c.orig] = c.name;
		});

		var selectionOrder = [];
		displayOrder.forEach(function(orig) {
			var meta = layout.cols.filter(function(c) { return c.orig === orig; })[0];
			if (!meta || !meta.selectable) return;
			var cur = dtCurrentFromOrig(table, orig);
			if (table.column(cur).visible()) {
				selectionOrder.push(orig);
			}
		});

		$modal.data('dt-table', table);
		$modal.data('layout', layout);
		$modal.data('nameByOrig', nameByOrig);
		$modal.data('selectionOrder', selectionOrder.slice());

		var $box = $modal.find('.dt-col-modal-checkboxes');
		$box.empty();
		var $selectAllRow = $('<div class="form-check mb-2 pb-2 border-bottom"></div>');
		$selectAllRow.append(
			$('<input type="checkbox" class="form-check-input dt-col-select-all" id="dt-col-select-all" />')
		);
		$selectAllRow.append(
			$('<label class="form-check-label font-weight-bold" for="dt-col-select-all"></label>').text('Select all')
		);
		$box.append($selectAllRow);
		var selectableDisplayOrder = displayOrder.filter(function(orig) {
			var meta = layout.cols.filter(function(c) { return c.orig === orig; })[0];
			return meta && meta.selectable;
		});
		selectableDisplayOrder.forEach(function(orig) {
			var meta = layout.cols.filter(function(c) { return c.orig === orig; })[0];
			var checked = selectionOrder.indexOf(orig) !== -1;
			var id = 'dt-col-cb-' + orig;
			var $row = $('<div class="form-check mb-1"></div>');
			$row.append(
				$('<input type="checkbox" class="form-check-input dt-col-cb" />')
					.attr('id', id)
					.attr('data-orig', orig)
					.prop('checked', checked)
			);
			$row.append($('<label class="form-check-label"></label>').attr('for', id).text(meta.name));
			$box.append($row);
		});

		updateDtColumnModalOrderList($modal);
		syncDtColumnSelectAllState($modal);
	}

	function applyDtColumnOrderModal() {
		var $modal = $('#dtColumnOrderModal');
		var table = $modal.data('dt-table');
		var layout = $modal.data('layout');
		var selectionOrder = $modal.data('selectionOrder') || [];
		if (!table || !layout) return;

		var selectableOrigs = layout.cols.filter(function(c) { return c.selectable; }).map(function(c) { return c.orig; });
		var hiddenSelectable = selectableOrigs.filter(function(o) {
			return selectionOrder.indexOf(o) === -1;
		});

		var used = {};
		function addUnique(arr, o) {
			if (o === null || o === undefined || used[o]) return;
			used[o] = true;
			arr.push(o);
		}

		var fullOrder = [];
		if (layout.srNoOrig !== null) addUnique(fullOrder, layout.srNoOrig);
		selectionOrder.forEach(function(o) { addUnique(fullOrder, o); });
		hiddenSelectable.forEach(function(o) { addUnique(fullOrder, o); });

		var displayOrder = getDtDisplayOrderOriginals(table);
		displayOrder.forEach(function(orig) {
			addUnique(fullOrder, orig);
		});

		if (layout.actionOrig !== null) {
			fullOrder = fullOrder.filter(function(o) { return o !== layout.actionOrig; });
			fullOrder.push(layout.actionOrig);
		}

		if (table.colReorder && typeof table.colReorder.order === 'function') {
			table.colReorder.order(fullOrder, true);
		}

		var visibleSet = {};
		selectionOrder.forEach(function(o) { visibleSet[o] = true; });
		layout.cols.forEach(function(c) {
			var cur = dtCurrentFromOrig(table, c.orig);
			if (c.selectable) {
				table.column(cur).visible(!!visibleSet[c.orig], false);
			} else {
				table.column(cur).visible(true, false);
			}
		});

		table.columns.adjust().draw(false);
		$modal.modal('hide');
	}

	function bindDtColumnOrderModalOnce() {
		if (_dtColumnOrderModalBound) return;
		_dtColumnOrderModalBound = true;
		$(document).on('change', '#dtColumnOrderModal .dt-col-cb', function() {
			var $modal = $('#dtColumnOrderModal');
			var orig = parseInt($(this).attr('data-orig'), 10);
			var order = $modal.data('selectionOrder') || [];
			if ($(this).is(':checked')) {
				if (order.indexOf(orig) === -1) order.push(orig);
			} else {
				order = order.filter(function(o) { return o !== orig; });
			}
			$modal.data('selectionOrder', order);
			updateDtColumnModalOrderList($modal);
			syncDtColumnSelectAllState($modal);
		});
		$(document).on('change', '#dtColumnOrderModal .dt-col-select-all', function() {
			var $modal = $('#dtColumnOrderModal');
			var checked = $(this).is(':checked');
			var $cbs = $modal.find('.dt-col-cb');
			if (checked) {
				var order = [];
				$cbs.each(function() {
					$(this).prop('checked', true);
					order.push(parseInt($(this).attr('data-orig'), 10));
				});
				$modal.data('selectionOrder', order);
			} else {
				$cbs.prop('checked', false);
				$modal.data('selectionOrder', []);
			}
			updateDtColumnModalOrderList($modal);
		});
		$(document).on('click', '#dtColumnOrderModal .dt-col-modal-generate-btn', function() {
			applyDtColumnOrderModal();
		});
	}

	function getDatatablePrintLetterheadInner(logoUrl) {
		return '<div style="width:100%;display:flex;justify-content:center;box-sizing:border-box;">' +
			'<div style="display:flex;align-items:flex-start;justify-content:flex-start;gap:12px 22px;color:#111;font-family:Arial,Helvetica,sans-serif;text-align:left;box-sizing:border-box;max-width:100%;">' +
			'<img src="' + logoUrl + '" alt="" style="display:block;width:118px;max-width:28vw;min-width:72px;height:auto;max-height:92px;object-fit:contain;flex:0 0 auto;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact;" />' +
			'<div style="flex:0 1 auto;min-width:120px;max-width:520px;font-size:10px;line-height:1.38;text-align:left;align-self:flex-start;">' +
			'<div style="font-size:15px;font-weight:bold;letter-spacing:0.02em;line-height:1.15;margin:0;">HERAMB INDUSTRIES</div>' +
			'<div style="font-size:11px;font-weight:bold;margin-top:5px;line-height:1.2;">Sales - On-Grid / Off-Grid Solar</div>' +
			'<div style="margin-top:7px;font-size:10px;line-height:1.35;"><span style="font-weight:bold;">REGD ADDRESS :</span> Bhagya Bangla, Block No. 2, Opp - Sant Eknamth Mandir, New Osmanpura, Chh. Sambhaji Nagar. Maharashtra, 431001</div>' +
			'<div style="margin-top:6px;font-size:10px;line-height:1.35;"><span style="font-weight:bold;">EMAIL :</span> herambasd1@gmail.com &nbsp; <span style="font-weight:bold;">GSTIN/UIN :</span> 27AIPPD9639R1Z6</div>' +
			'</div></div></div>';
	}

	function attachGlobalDatatableTools(table) {
		var $wrapper = $(table.table().container());
		var $lengthBox = $wrapper.find('.dataTables_length');
		if (!$lengthBox.length || $lengthBox.find('.column-filter-wrap').length) return;

		var minimalToolsOnly = $(table.table().node()).hasClass('dt-tools-minimal');
		var exportButtonsHtml = minimalToolsOnly ? '' : (
			  '<button type="button" class="table-tool-btn toolbarExcelBtn" title="Excel"><i class="fa fa-file-excel"></i></button>' +
			  '<button type="button" class="table-tool-btn toolbarPdfBtn" title="PDF"><i class="fa fa-file-pdf"></i></button>' +
			  '<button type="button" class="table-tool-btn toolbarCopyBtn" title="Copy"><i class="fa fa-copy"></i></button>' +
			  '<button type="button" class="table-tool-btn toolbarPrintBtn" title="Print"><i class="fa fa-print"></i></button>'
		);

		var selectorHtml = '' +
			'<div class="dt-global-tools column-filter-wrap">' +
			  exportButtonsHtml +
			  '<button type="button" class="table-tool-btn columnFilterOpenBtn" title="Columns"><i class="fa fa-list"></i></button>' +
			  '<button type="button" class="table-tool-btn resetColumnsBtn" title="Refresh"><i class="fa fa-refresh"></i></button>' +
			'</div>';
		$lengthBox.append(selectorHtml);

		$lengthBox.on('click', '.table-tool-btn', function() {
			var $btn = $(this);
			$btn.addClass('is-active');
			setTimeout(function() { $btn.removeClass('is-active'); }, 350);
		});

		$lengthBox.on('click', '.columnFilterOpenBtn', function() {
			bindDtColumnOrderModalOnce();
			populateDtColumnOrderModal(table);
			$('#dtColumnOrderModal').modal('show');
		});

		$lengthBox.on('click', '.resetColumnsBtn', function() {
			table.columns().every(function() {
				var idx = this.index();
				var name = ($(table.column(idx).header()).text() || '').trim();
				if (name && name !== 'Sr No.' && name !== 'Action') {
					this.visible(true, false);
				}
			});
			if (table.colReorder && typeof table.colReorder.reset === 'function') table.colReorder.reset();
			table.columns.adjust().draw(false);
		});

		$lengthBox.on('click', '.toolbarExcelBtn', function() {
			if (typeof XLSX === 'undefined') { alert('Excel library not loaded.'); return; }
			var data = getExportDataForTable(table);
			var headerLines = getCompanyHeaderLines();
			data.unshift([]);
			data.unshift([headerLines[1]]);
			data.unshift([headerLines[0]]);
			var ws = XLSX.utils.aoa_to_sheet(data);
			var wb = XLSX.utils.book_new();
			XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
			XLSX.writeFile(wb, 'table.xlsx');
		});
		$lengthBox.on('click', '.toolbarCopyBtn', function() {
			var data = getExportDataForTable(table);
			var txt = data.map(function(r){ return r.join('\t'); }).join('\n');
			var ta = document.createElement('textarea');
			ta.textContent = txt;
			document.body.appendChild(ta);
			ta.select();
			document.execCommand('copy');
			document.body.removeChild(ta);
		});
		$lengthBox.on('click', '.toolbarPrintBtn', function() {
			var data = getExportDataForTable(table);
			var logoUrl = window.location.origin + '/static/images/db_logo_200.png';
			var colCount = data[0] ? data[0].length : 1;
			var letterRow = '<tr class="dt-print-letterhead"><td colspan="' + colCount + '" style="border:none!important;padding:0 0 16px 0!important;vertical-align:top;background:#fff;">' +
				getDatatablePrintLetterheadInner(logoUrl) + '</td></tr>';
			var headRow = '<tr>' + data[0].map(function(h) { return '<th>' + h + '</th>'; }).join('') + '</tr>';
			var bodyRows = data.slice(1).map(function(row) {
				return '<tr>' + row.map(function(c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
			}).join('');
			var w = window.open('', '_blank');
			w.document.open();
			w.document.write('<html><head><title>Print</title>');
			w.document.write('<style>body{margin:12px;font-family:Arial,Helvetica,sans-serif;}table.dt-print-main{width:100%;border-collapse:collapse;}thead{display:table-header-group;}tr.dt-print-letterhead td{border:none!important;}thead tr:not(.dt-print-letterhead) th{border:1px solid #333;padding:6px;background:#eee;font-weight:bold;font-size:11px;}tbody td{border:1px solid #333;padding:4px;font-size:11px;}@media print{thead{display:table-header-group;}tr.dt-print-letterhead td{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}</style>');
			w.document.write('</head><body>');
			w.document.write('<table class="dt-print-main" border="0"><thead>' + letterRow + headRow + '</thead><tbody>' + bodyRows + '</tbody></table>');
			w.document.write('</body></html>');
			w.document.close();
			w.print();
		});
		$lengthBox.on('click', '.toolbarPdfBtn', function() {
			if (typeof jsPDF === 'undefined' && !(window.jspdf && window.jspdf.jsPDF)) { alert('PDF library not loaded.'); return; }
			var PDFCtor = (window.jspdf && window.jspdf.jsPDF) ? window.jspdf.jsPDF : jsPDF;
			var pdf = new PDFCtor();
			var headerLines = getCompanyHeaderLines();
			var data = getExportDataForTable(table);
			var head = [data[0]];
			var body = data.slice(1);
			pdf.setFontSize(15);
			pdf.text(headerLines[0], 14, 14);
			pdf.setFontSize(10);
			pdf.text(headerLines[1], 14, 20);
			if (typeof pdf.autoTable === 'function') {
				pdf.autoTable({
					head: head,
					body: body,
					startY: 26,
					theme: 'grid',
					styles: { fontSize: 8, cellPadding: 2, textColor: [33, 33, 33], cellWidth: 'wrap', overflow: 'linebreak', halign: 'left', valign: 'top' },
					bodyStyles: { halign: 'left', valign: 'top' },
					headStyles: { fillColor: [238, 238, 238], textColor: [0, 0, 0], fontStyle: 'bold', halign: 'left', valign: 'top' },
					tableWidth: 'wrap',
					columnStyles: { 0: { cellWidth: 12 } }
				});
			} else if (window.jspdf && typeof window.jspdf.autoTable === 'function') {
				window.jspdf.autoTable(pdf, {
					head: head,
					body: body,
					startY: 26,
					theme: 'grid',
					styles: { fontSize: 8, cellPadding: 2, textColor: [33, 33, 33], cellWidth: 'wrap', overflow: 'linebreak', halign: 'left', valign: 'top' },
					bodyStyles: { halign: 'left', valign: 'top' },
					headStyles: { fillColor: [238, 238, 238], textColor: [0, 0, 0], fontStyle: 'bold', halign: 'left', valign: 'top' },
					tableWidth: 'wrap',
					columnStyles: { 0: { cellWidth: 12 } }
				});
			} else {
				var fallbackRows = [data[0]].concat(body.slice(0, 45));
				var pageWidth = pdf.internal.pageSize.getWidth();
				var startX = 10;
				var startY = 28;
				var usableWidth = pageWidth - (startX * 2);
				var colCount = Math.max((data[0] || []).length, 1);
				var colWidth = usableWidth / colCount;
				var rowHeight = 7;
				var currentY = startY;
				pdf.setFontSize(8);
				fallbackRows.forEach(function(row, rowIdx) {
					if (currentY + rowHeight > (pdf.internal.pageSize.getHeight() - 10)) {
						pdf.addPage();
						currentY = 14;
					}
					if (rowIdx === 0) {
						pdf.setFillColor(238, 238, 238);
					}
					row.forEach(function(cell, colIndex) {
						var x = startX + (colIndex * colWidth);
						var safeText = String(cell || '').replace(/\s+/g, ' ').trim();
						if (rowIdx === 0) pdf.rect(x, currentY - 5, colWidth, rowHeight, 'FD');
						else pdf.rect(x, currentY - 5, colWidth, rowHeight);
						if (rowIdx === 0) pdf.setFont(undefined, 'bold');
						else pdf.setFont(undefined, 'normal');
						var clipped = pdf.splitTextToSize(safeText, colWidth - 2);
						pdf.text(clipped.slice(0, 1), x + 1, currentY);
					});
					currentY += rowHeight;
				});
			}
			pdf.save('table.pdf');
		});
	}

	window.attachGlobalDatatableTools = attachGlobalDatatableTools;

	if ($('.datatable').length > 0 && $.fn.DataTable) {
		$('table.datatable').each(function() {
			var $tbl = $(this);
			// scrollX splits header/body into separate tables and often misaligns columns;
			// use Bootstrap .table-responsive on wide tables instead.
			var compactCols = $tbl.hasClass('dt-compact-cols');
			var dt = $.fn.dataTable.isDataTable(this) ? $tbl.DataTable() : $tbl.DataTable({
				scrollX: false,
				colReorder: true,
				autoWidth: !compactCols,
				pageLength: 10,
				lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
				language: { lengthMenu: 'Show _MENU_ rows' }
			});
			attachGlobalDatatableTools(dt);
			dt.columns.adjust().draw(false);
			var $dtWrapper = $tbl.closest('.dataTables_wrapper');
			var $tableEl = $dtWrapper.children('table.dataTable').first();
			if (!$tableEl.length) {
				$tableEl = $dtWrapper.find('table.dataTable').first();
			}
			if ($tableEl.length && !$tableEl.parent().hasClass('dt-table-scroll-x') && !$tbl.hasClass('dt-no-hscroll')) {
				$tableEl.wrap('<div class="dt-table-scroll-x"></div>');
				dt.columns.adjust();
			}
		});
		$(window).on('load resize', function() {
			$('table.datatable').each(function() {
				if ($.fn.dataTable.isDataTable(this)) {
					$(this).DataTable().columns.adjust();
				}
			});
		});
	}

	// Check all email
	
	$(document).on('click', '#check_all', function() {
		$('.checkmail').click();
		return false;
	});
	if($('.checkmail').length > 0) {
		$('.checkmail').each(function() {
			$(this).on('click', function() {
				if($(this).closest('tr').hasClass('checked')) {
					$(this).closest('tr').removeClass('checked');
				} else {
					$(this).closest('tr').addClass('checked');
				}
			});
		});
	}
	
	// Mail important
	
	$(document).on('click', '.mail-important', function() {
		$(this).find('i.fa').toggleClass('fa-star').toggleClass('fa-star-o');
	});
	
	// Summernote
	
	if($('.summernote').length > 0) {
		$('.summernote').summernote({
			height: 200,                 // set editor height
			minHeight: null,             // set minimum height of editor
			maxHeight: null,             // set maximum height of editor
			focus: false                 // set focus to editable area after initializing summernote
		});
	}
	
	
	// Sidebar Slimscroll

	if($slimScrolls.length > 0) {
		$slimScrolls.slimScroll({
			height: 'auto',
			width: '100%',
			position: 'right',
			size: '7px',
			color: '#ccc',
			allowPageScroll: false,
			wheelStep: 10,
			touchScrollStep: 100
		});
		var wHeight = $(window).height() - 0;
		$slimScrolls.height(wHeight);
		$('.sidebar .slimScrollDiv').height(wHeight);
		$(window).resize(function() {
			var rHeight = $(window).height() - 0;
			$slimScrolls.height(rHeight);
			$('.sidebar .slimScrollDiv').height(rHeight);
		});
		// After slimScroll wraps the sidebar, re-apply open state (complaint pages, etc.)
		expandSidebarActiveBranches();
	}

	$(window).on('load', function() {
		expandSidebarActiveBranches();
	});
	
	// Small Sidebar

	$(document).on('click', '#toggle_btn', function() {
		if($('body').hasClass('mini-sidebar')) {
			$('body').removeClass('mini-sidebar');
			$('.subdrop + ul').slideDown();
		} else {
			$('body').addClass('mini-sidebar');
			$('.subdrop + ul').slideUp();
		}
		setTimeout(function(){ 
			mA.redraw();
			mL.redraw();
		}, 300);
		return false;
	});
	// Mini-sidebar hover: only when Preskool mini-sidebar + toggle is used (not AdminLTE-only).
	// Document-level mouseover was collapsing submenus while moving from parent link into the dropdown.
	$(document).on('mouseenter.sidemenu', '.sidebar', function() {
		if ($('body').hasClass('mini-sidebar') && $('#toggle_btn').is(':visible')) {
			$('body').addClass('expand-menu');
			$('.subdrop + ul').stop(true, true).slideDown(150);
		}
	});
	$(document).on('mouseleave.sidemenu', '.sidebar', function() {
		if ($('body').hasClass('mini-sidebar') && $('#toggle_btn').is(':visible')) {
			$('body').removeClass('expand-menu');
			$('.subdrop + ul').stop(true, true).slideUp(150);
		}
	});

	// Circle Progress Bar
	function animateElements() {
		$('.circle-bar1').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph1').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph1').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
		$('.circle-bar2').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph2').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph2').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
		$('.circle-bar3').each(function () {
			var elementPos = $(this).offset().top;
			var topOfWindow = $(window).scrollTop();
			var percent = $(this).find('.circle-graph3').attr('data-percent');
			var animate = $(this).data('animate');
			if (elementPos < topOfWindow + $(window).height() - 30 && !animate) {
				$(this).data('animate', true);
				$(this).find('.circle-graph3').circleProgress({
					value: percent / 100,
					size : 400,
					thickness: 30,
					fill: {
						color: '#6e6bfa'
					}
				});
			}
		});
	}	
	
	if($('.circle-bar').length > 0) {
		animateElements();
	}
	$(window).scroll(animateElements);
	
	// Preloader
	
	$(window).on('load', function () {
		if($('#loader').length > 0) {
			$('#loader').delay(350).fadeOut('slow');
			$('body').delay(350).css({ 'overflow': 'visible' });
		}
	})

	// Modal close fallback: keeps close/X working even with mixed Bootstrap scripts.
	function forceHideModal($modal) {
		if (!$modal || !$modal.length) {
			return;
		}
		$modal.removeClass('show').hide().attr('aria-hidden', 'true');
		$modal.removeAttr('aria-modal');
		$('body').removeClass('modal-open').css('padding-right', '');
		$('.modal-backdrop').remove();
	}

	$(document).on('click', '[data-dismiss="modal"], [data-bs-dismiss="modal"], .modal .close, .modal .btn-close', function() {
		var $btn = $(this);
		var target = $btn.attr('data-target') || $btn.attr('data-bs-target');
		var $modal = target ? $(target) : $btn.closest('.modal');

		if (window.jQuery && $.fn && typeof $.fn.modal === 'function') {
			try {
				$modal.modal('hide');
			} catch (e) {
				forceHideModal($modal);
			}
		} else {
			forceHideModal($modal);
		}
	});
	
})(jQuery);