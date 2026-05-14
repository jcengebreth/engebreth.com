export interface AppConfig {
	metadata: {
		stage: string;
		project_name: string;
	};
	dns: {
		fqdn: string;
	};
}
