import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth';

@Injectable({ providedIn: 'root' })
export class BackupService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  
  private apiUrl = `${environment.apiUrl}/api/backup`; 

  generarBackupManual(): Observable<HttpResponse<Blob>> {
    const token = this.authService.obtenerToken();
    const headers = token ? new HttpHeaders({ 'Authorization': `Bearer ${token}` }) : new HttpHeaders();

    return this.http.get(`${this.apiUrl}/manual`, {
      headers,
      observe: 'response', 
      responseType: 'blob' 
    });
  }
}