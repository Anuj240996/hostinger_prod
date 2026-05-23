document.addEventListener('DOMContentLoaded', function(){
  const addBtn = document.getElementById('add-activity-btn');
  const submitBtn = document.getElementById('submitActivity');
  const activityModal = document.getElementById('activityModal');
  if (!addBtn || !submitBtn) return;

  // Submit activity from modal
  submitBtn.addEventListener('click', function(e){
    const typeEl = document.getElementById('activityType');
    const noteEl = document.getElementById('activityNote');
    const type = typeEl ? typeEl.value : 'note';
    const note = noteEl ? noteEl.value.trim() : '';
    // basic validation
    if (!note) {
      if (!confirm('Add empty note?')) return;
    }
    // extract lead pk from URL
    const parts = window.location.pathname.split('/');
    const pk = parts.filter(Boolean).pop();
    fetch(`/leads/${pk}/activity/add/`, {
      method: 'POST',
      headers: {'X-CSRFToken': (document.querySelector('meta[name="csrf-token"]')||{}).content || ''},
      body: new URLSearchParams({note: note, type: type})
    }).then(r=>r.json()).then(data=>{
      if (data.status === 'ok') {
        // hide modal if bootstrap present
        try {
          const modal = bootstrap.Modal.getInstance(activityModal);
          if (modal) modal.hide();
        } catch {}
        // update timeline DOM and status without full reload
        try {
          const timeline = document.getElementById('timeline');
          if (timeline) {
            const item = document.createElement('div');
            item.className = 'timeline-item';
            const timeDiv = document.createElement('div');
            timeDiv.className = 'time';
            // format timestamp or use raw
            const dt = new Date(data.created_at);
            timeDiv.textContent = dt.toLocaleString();
            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'body';
            const typeMap = {'call':'Call','whatsapp':'WhatsApp','email':'Email','note':'Note','visit':'Site Visit','quotation':'Quotation','conversion':'Conversion'};
            const typeLabel = typeMap[data.type] || data.type;
            bodyDiv.innerHTML = `<strong>${typeLabel}</strong> — ${data.note || ''}`;
            const metaDiv = document.createElement('div');
            metaDiv.className = 'meta small text-muted';
            metaDiv.textContent = `By ${data.user || 'System'}`;
            item.appendChild(timeDiv);
            item.appendChild(bodyDiv);
            item.appendChild(metaDiv);
            // prepend
            timeline.insertBefore(item, timeline.firstChild);
          }
          // update status display if present (note backend sets status mapping)
          const statusEl = document.getElementById('leadStatus');
          if (statusEl) {
            // map type -> status label roughly
            const statusMap = {'call':'Contacted','whatsapp':'Contacted','visit':'Survey Scheduled','quotation':'Quoted','conversion':'Booked','note': statusEl.textContent};
            statusEl.textContent = statusMap[data.type] || statusEl.textContent;
          }
          const scoreEl = document.getElementById('leadScore');
          if (scoreEl) {
            // optional: bump score locally (server source of truth)
            // scoreEl.textContent = parseInt(scoreEl.textContent||'0') + 1;
          }
        } catch (e) {
          // fallback
          window.location.reload();
        }
      } else {
        alert('Failed to add activity');
      }
    }).catch(()=>alert('Network error'));
  });
});

