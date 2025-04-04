<template>
    <li class="nav-item dropdown">
      <a class="nav-link dropdown-toggle" href="#" id="layoutDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
        Layout
      </a>
      <ul class="dropdown-menu" aria-labelledby="layoutDropdown">
        <li><a class="dropdown-item" href="#" @click="openSaveLayoutModal">Save Current Layout</a></li>
        <li><a class="dropdown-item" href="#" @click="openRenameLayoutModal">Rename Layout</a></li>
        <li><hr class="dropdown-divider"></li>
        <li><h6 class="dropdown-header">Stored Layouts</h6></li>
        <li v-if="storedLayouts.length === 0"><a class="dropdown-item disabled">No layouts saved yet</a></li>
        <li v-for="layout in storedLayouts" :key="layout.id">
          <div class="d-flex justify-content-between align-items-center">
            <a class="dropdown-item" href="#" @click="activateLayout(layout.id)">{{ layout.name }}</a>
            <div>
              <button class="btn btn-sm btn-outline-primary me-1" @click="activateLayout(layout.id)" title="Activate">
                <i class="bi bi-play-fill"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteLayout(layout.id)" title="Delete">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </li>
      </ul>
  
      <div class="modal fade" id="saveLayoutModal" tabindex="-1" aria-labelledby="saveLayoutModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="saveLayoutModalLabel">Save Layout</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label for="layoutName" class="form-label">Layout Name:</label>
                <input type="text" class="form-control" id="layoutName" v-model="newLayoutName" placeholder="Enter layout name">
              </div>
              <div v-if="existingLayouts.length > 0">
                <label for="overwriteLayout" class="form-label">Overwrite Existing Layout (Optional):</label>
                <select class="form-select" id="overwriteLayout" v-model="overwriteLayoutId">
                  <option value="">-- Select Layout to Overwrite --</option>
                  <option v-for="layout in existingLayouts" :key="layout.id" :value="layout.id">{{ layout.name }}</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="saveCurrentLayout">Save</button>
            </div>
          </div>
        </div>
      </div>
  
      <div class="modal fade" id="renameLayoutModal" tabindex="-1" aria-labelledby="renameLayoutModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="renameLayoutModalLabel">Rename Layout</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3" v-if="selectedLayoutToRename">
                <label for="renameLayoutName" class="form-label">New Layout Name for "{{ selectedLayoutToRename.name }}":</label>
                <input type="text" class="form-control" id="renameLayoutName" v-model="renameLayoutName" placeholder="Enter new name">
              </div>
              <div v-else>
                <p>Please select a layout to rename from the dropdown.</p>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="renameSelectedLayout" :disabled="!renameLayoutName">Rename</button>
            </div>
          </div>
        </div>
      </div>
    </li>
  </template>
  
  <script>
  import { Modal } from 'bootstrap'; // Import Bootstrap Modal
  
  export default {
    data() {
      return {
        storedLayouts: [
          { id: 1, name: 'Default Layout' },
          { id: 2, name: 'Dashboard View' },
        ], // Example stored layouts
        newLayoutName: '',
        overwriteLayoutId: '',
        selectedLayoutToRename: null,
        renameLayoutName: '',
        saveLayoutModalInstance: null,
        renameLayoutModalInstance: null,
      };
    },
    computed: {
      existingLayouts() {
        return this.storedLayouts; // For simplicity, all stored layouts are available for overwriting
      },
    },
    mounted() {
      this.saveLayoutModalInstance = new Modal(document.getElementById('saveLayoutModal'));
      this.renameLayoutModalInstance = new Modal(document.getElementById('renameLayoutModal'));
    },
    methods: {
      openSaveLayoutModal() {
        this.newLayoutName = '';
        this.overwriteLayoutId = '';
        this.saveLayoutModalInstance.show();
      },
      openRenameLayoutModal() {
        this.renameLayoutName = '';
        this.selectedLayoutToRename = null;
        // You might want to provide a way to select which layout to rename
        // For this example, we'll assume the user will trigger this from the "Stored Layouts" list
        // Or you could have a separate dropdown to select the layout to rename here.
        // For simplicity, we'll just open the modal and rely on the user knowing which to rename.
        this.renameLayoutModalInstance.show();
      },
      saveCurrentLayout() {
        if (this.newLayoutName || this.overwriteLayoutId) {
          if (this.overwriteLayoutId) {
            // Logic to overwrite the layout with ID this.overwriteLayoutId
            const index = this.storedLayouts.findIndex(layout => layout.id === parseInt(this.overwriteLayoutId));
            if (index !== -1) {
              this.storedLayouts[index].name = this.newLayoutName || this.storedLayouts[index].name + ' (Overwritten)';
              alert(`Layout "${this.storedLayouts[index].name}" overwritten.`);
            } else {
              alert('Error: Layout to overwrite not found.');
            }
          } else if (this.newLayoutName) {
            const newId = this.storedLayouts.length > 0 ? Math.max(...this.storedLayouts.map(l => l.id)) + 1 : 1;
            this.storedLayouts.push({ id: newId, name: this.newLayoutName });
            alert(`Layout "${this.newLayoutName}" saved.`);
          }
          this.saveLayoutModalInstance.hide();
          this.newLayoutName = '';
          this.overwriteLayoutId = '';
        } else {
          alert('Please enter a name for the layout.');
        }
        // In a real application, you would send the current layout data to a server or store it locally.
        console.log('Saving layout with name:', this.newLayoutName, 'Overwriting ID:', this.overwriteLayoutId);
      },
      openRenameLayoutModalFor(layout) {
        this.selectedLayoutToRename = layout;
        this.renameLayoutName = layout.name;
        this.renameLayoutModalInstance.show();
      },
      renameSelectedLayout() {
        if (this.selectedLayoutToRename && this.renameLayoutName) {
          this.selectedLayoutToRename.name = this.renameLayoutName;
          alert(`Layout renamed to "${this.renameLayoutName}".`);
          this.renameLayoutModalInstance.hide();
          this.selectedLayoutToRename = null;
          this.renameLayoutName = '';
        } else {
          alert('Please select a layout and enter a new name.');
        }
        // In a real application, you would update the layout name in your data store.
        console.log('Renaming layout:', this.selectedLayoutToRename, 'to:', this.renameLayoutName);
      },
      activateLayout(layoutId) {
        const layout = this.storedLayouts.find(l => l.id === layoutId);
        if (layout) {
          alert(`Activating layout: ${layout.name} (ID: ${layout.id})`);
          // In a real application, you would load the layout data associated with this ID.
          console.log('Activating layout:', layout);
        }
      },
      deleteLayout(layoutId) {
        if (confirm('Are you sure you want to delete this layout?')) {
          this.storedLayouts = this.storedLayouts.filter(layout => layout.id !== layoutId);
          alert(`Layout with ID ${layoutId} deleted.`);
          // In a real application, you would remove the layout from your data store.
          console.log('Deleting layout with ID:', layoutId);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  /* Optional: Add any component-specific styling here */
  .dropdown-item .btn {
    padding: 0.1rem 0.25rem;
    margin: 0;
  }
  </style>