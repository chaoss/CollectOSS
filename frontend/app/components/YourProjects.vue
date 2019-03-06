<template>
<div>
			<h4 style="text-align: center;"><b>Current Projects:</b></h4>
	<span style="align-content: center !important;">
		<div class="row auto" style="text-align: center !important;">
			<label class="col col-3"><h3>Twitter</h3></label>
			<div class="col col-2"><edit-project></edit-project></div>
			<div class="col col-2"><remove-project></remove-project></div>
		</div>
		<div class="row auto" style="text-align: center;">
			<label class="col col-3"><h3>Pulp</h3></label>
			<div class="col col-2"><edit-project></edit-project></div>
			<div class="col col-2"><remove-project></remove-project></div>
		</div>
		<div class="row auto" style="text-align: center;">
			<label class="col col-3"><h3>Etc</h3></label>
			<div class="col col-2"><edit-project></edit-project></div>
			<div class="col col-2"><remove-project></remove-project></div>
		</div>
		<div class="row auto" style="text-align: center !important;">
			<add-new-project></add-new-project>
		</div>
	</span>
</div>

</template>

<script type="text/javascript">
	import AddNewProject from './AddNewProject'
	import EditProject from './EditProject'
	import RemoveProject from './RemoveProject'
	module.exports = {
		components: {
			AddNewProject,
			EditProject,
			RemoveProject
		}
	}
</script>
