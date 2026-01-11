function createModalContainer() {
  if (document.getElementById('customModal')) {
    return;
  }
  
  const modalHTML = `
    <div id="customModal" class="modal-overlay hidden">
      <div class="modal-content">
        <div class="modal-title" id="modalTitle">Notice</div>
        <div class="modal-message" id="modalMessage"></div>
        <div class="modal-buttons">
          <button class="modal-btn modal-btn-primary" id="modalOkBtn">OK</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  console.log('Modal container created');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', createModalContainer);
} else {
  createModalContainer();
}

function showModal(message, title = "Notice") {
  if (!document.getElementById('customModal')) {
    createModalContainer();
    setTimeout(() => showModal(message, title), 10);
    return;
  }
  
  const modal = document.getElementById('customModal');
  const titleEl = document.getElementById('modalTitle');
  const messageEl = document.getElementById('modalMessage');
  const okBtn = document.getElementById('modalOkBtn');
  
  if (!modal || !titleEl || !messageEl || !okBtn) {
    console.error('Modal elements not found, falling back to alert');
    alert(message);
    return;
  }
  
  titleEl.textContent = title;
  messageEl.textContent = message;
  modal.classList.remove('hidden');
  
  okBtn.onclick = () => {
    modal.classList.add('hidden');
  };
  
  modal.onclick = (e) => {
    if (e.target === modal) {
      modal.classList.add('hidden');
    }
  };
}

function showConfirm(message, title = "Confirm", onConfirm, onCancel) {
  let confirmModal = document.getElementById('customConfirmModal');
  
  if (!confirmModal) {
    const confirmHTML = `
      <div id="customConfirmModal" class="modal-overlay hidden">
        <div class="modal-content">
          <div class="modal-title" id="confirmModalTitle">Confirm</div>
          <div class="modal-message" id="confirmModalMessage"></div>
          <div class="modal-buttons">
            <button class="modal-btn modal-btn-secondary" id="confirmCancelBtn">Cancel</button>
            <button class="modal-btn modal-btn-primary" id="confirmOkBtn">OK</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', confirmHTML);
    confirmModal = document.getElementById('customConfirmModal');
  }
  
  const titleEl = document.getElementById('confirmModalTitle');
  const messageEl = document.getElementById('confirmModalMessage');
  const okBtn = document.getElementById('confirmOkBtn');
  const cancelBtn = document.getElementById('confirmCancelBtn');
  
  if (!titleEl || !messageEl || !okBtn || !cancelBtn) {
    console.error('Confirm modal elements not found, falling back to confirm');
    const result = confirm(message);
    if (result && onConfirm) onConfirm();
    else if (!result && onCancel) onCancel();
    return;
  }
  
  titleEl.textContent = title;
  messageEl.textContent = message;
  confirmModal.classList.remove('hidden');
  
  okBtn.onclick = () => {
    confirmModal.classList.add('hidden');
    if (onConfirm) onConfirm();
  };
  
  cancelBtn.onclick = () => {
    confirmModal.classList.add('hidden');
    if (onCancel) onCancel();
  };
  
  confirmModal.onclick = (e) => {
    if (e.target === confirmModal) {
      confirmModal.classList.add('hidden');
      if (onCancel) onCancel();
    }
  };
}

export { createModalContainer, showModal, showConfirm };