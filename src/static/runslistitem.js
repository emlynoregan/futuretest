Vue.component('runs-list-item', {
  props: [
	 "inrun"
  ],
  data: function() 
  {
	  return {
		  run: null,
		  timer: null
	  }
  },
  computed: {
	run_is_complete: function(){
		return this.run && (["pass", "fail"].indexOf(this.run.status) >= 0);
	},
	run_is_underway: function(){
		return this.run && (["underway", "pass", "fail"].indexOf(this.run.status) >= 0);
	}  
  },
  template: `
	  <div>
		  <div>{{run.id}} ({{run.testname}}): {{run.status}}</div>
		  <div v-if="run_is_underway">
		  	<span>started: {{run.started_desc}}</span>
		  	<span>progress: {{run.progress}}</span>
		  	<span v-if="run.final_runtime_usec">completed: {{run.final_runtime_usec / 1000000}} sec</span>
		  	<span v-if="run.final_message">message: {{run.final_message}}</span>
		  </div>
	  </div>
  `,
  methods: {
    reload_run: function() {
		var _app = this;

		_app.$http.get('/megatest/runs', {params: {id: _app.run.id}}).then
        (
		    function (response) 
		    {
		    	console.log(response);
		    	
		    	if (response)
		    	{
		    		_app.run = response.body;
		    	}
		    }
		);
    },
	monitor_run: function() {
		  _app = this;
		  
		  if (_app.run && ["pre", "underway"].indexOf(_app.run.status) >= 0)
		  {
		  	if (!_app.timer)
		  	{
		  		_app.timer = setInterval(
		  			_app.reload_run,
		  			1000
		  		);
		  	}
		  }
		  else
		  {
		  	if (_app.timer)
		  	{
		  		clearTimeout(_app.timer);
		  		_app.timer = null;
		  	}
		  }
		}
  },
  created: function () {
	  this.run = this.inrun;
  },
  watch: {
	run: function(value) {
		this.monitor_run()
	}
  }
})