import cProfile, pstats, os

### http://stackoverflow.com/questions/5375624/a-decorator-that-profiles-a-method-call-and-logs-the-profiling-result ###
def profileit(scriptName):
    def inner(func):
        from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
        profiling = helpers.get_global_inputs().get('quali_profiling')
        reservation_context = helpers.get_reservation_context_details()
        reservation_id = reservation_context.id
        environment_name = reservation_context.environment_name
        def wrapper(*args, **kwargs):
            if not profiling:
                return func(*args, **kwargs)
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            s = open(os.path.join(profiling, scriptName + "_" + environment_name + "_" + reservation_id + ".text"), 'w')
            stats = pstats.Stats(prof, stream=s)
            stats.strip_dirs().sort_stats('cumtime').print_stats()
            return retval
        return wrapper
    return inner