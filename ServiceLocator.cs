using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Threading;
using Unity.VisualScripting;
using UnityEngine;

//Services
public interface IService
{
    
} 

public interface GetTheEarth : IService
{
    Transform Earth {get; set;}
}

public interface IMarkerManager : IService
{
     public MarkerSpot NewMarkerSpot{set;}
}
public interface IMarker : IService
{
    void ApplySpot(double latitude, double longitude);
}




[DefaultExecutionOrder(-100)]
public class ServiceLocator : MonoBehaviour
{
    Dictionary <string, IService> _services = new Dictionary<string, IService>();
    public static ServiceLocator Current;

    private void Awake()
    {
        CreateInstance();
    }

    private void CreateInstance()
    {
        if(Current != null && Current != this)
                Destroy(gameObject);
        
        Current = this;
    }

    public void Register<T>(T service) where T : IService
    {
       
        string key = typeof(T).Name;
        if (_services.ContainsKey(key))
        {
            Debug.LogError("already added");
            return;
        }

        Debug.Log("Process Go");

        _services.Add(key, service);
    }
    public void Unregister<T>() where T : IService
    {
        string key = typeof(T).Name;
        if (!_services.ContainsKey(key))
        {
            Debug.Log("attenpt to unregister not added service");
            return;
        }
        
        _services.Remove(key);
    }
    public T Get<T>() where T : IService
    {
        string key = typeof(T).Name;
        if (!_services.ContainsKey(key))
        {
            Debug.LogError("attempt to get following service" + key);
        
        } 

        return (T)_services[key];
    }


}
