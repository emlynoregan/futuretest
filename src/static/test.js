var Test = Vue.component('test', {
  data: function() {
	  return {
		  "statuses": ["underway", "pass", "fail"],
		  "runs": []
	  }
  },
  props: [ "testname" ],
  template: `
    <div>
	    <div @click="navtotests">(back to tests)</div>
	    <div>
		  <div>
		  	<span>Test: {{testname}}</span>
	  		<button @click="ongo">Go</button>
		  </div>
		  <div v-if="runs.length">
			  <ul>
				  <li v-for="run in runs" :key="run.id">
				  	<runs-list-item :inrun="run" />
				  </li>
			  </ul>
		  </div>
		  <div v-else>No runs</div>
		</div>
	</div>
  `,
  created: function () {
	  this.getRuns()
  },
  methods: {
	navtotests()
	{
		this.$router.push("/")
	},
    getRuns() 
    {
	  var lquery = {
		name: this.testname,
	    statuses: this.statuses
	  };
	  
      this.$http.get('/megatest/runs', {params: lquery}).then(
        function (response) 
	    {
	      this.runs = response.data;
	    }
      );
    },
    ongo()
    {
  	  var lquery = {
  		action: "go",
		name: this.testname
	  };

  	  var _app = this;
  	  
      this.$http.post('/megatest/tests', lquery).then(
        function (response) 
	    {
        	var id = response.data.id;
        	
        	console.log(id);

        	var numtries = 10;
        	function wait_for_run() {
	            _app.$http.get('/megatest/runs', {params: {id: id}}).then(
				    function (response) 
				    {
				    	console.log(response);
				    	
				    	if (response)// && (numtries <= 0))// || ["underway", "pass", "fail"].indexOf(response.body.status) >= 0))
				    	{
				        	_app.getRuns();
				    	}
				    	else
				    	{
				    		numtries--;
				    		setTimeout(
				    			wait_for_run,
				    			1000
				    		);
				    	}
				    }
				);
        	}
        	
        	wait_for_run();
	    }
      );
    }
  }
})